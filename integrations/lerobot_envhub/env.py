# Copyright 2026 The HuggingFace Inc. team. All rights reserved.
# Copyright 2026 RoboHand contributors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""EB300 adaptation of lerobot/so101-tabletop-mujoco@e68145d8.

Seven absolute position targets in radians, one full wrist image. Internal rack
joints are mechanical constraints, not actions. No IK, motor policy or teleoperator.
Local geometry must be restored as described in README.md before running.
"""

import json
from collections.abc import Mapping
from functools import partial
from pathlib import Path
from typing import Any

import gymnasium as gym
import mujoco
import numpy as np
from gymnasium import spaces

HERE = Path(__file__).absolute().parent
JOINT_NAMES = [*[f"J{i}.pos" for i in range(1, 7)], "MG995.pos"]
FPS = 25
LEROBOT_SIM = {
    "fps": FPS,
    "control_mode": "position",
    "semantics": "eb300-joint-radians-v1",
    "state_names": JOINT_NAMES,
    "action_names": JOINT_NAMES,
    "robot_type": "eb300",
}


class EB300Env(gym.Env):
    """Position-controlled EB300, with a free-tool contact/lift evaluator."""

    metadata = {"render_modes": ["rgb_array"], "render_fps": FPS}

    def __init__(
        self,
        scene: str | Path | None = None,
        fps: int = FPS,
        episode_length: int = 250,
        observation_height: int = 360,
        observation_width: int = 640,
        instruction: str = "Pick up the pencil and hold it above the table.",
        reset_keyframe: str | None = None,
        lift_height_m: float = 0.02,
        hold_seconds: float = 0.5,
        render_shadows: bool = True,
        terminate_on_success: bool = True,
    ):
        super().__init__()
        if fps != FPS:
            raise ValueError(f"EB300 contract is {FPS} Hz; do not silently change physics timestep")
        if min(episode_length, observation_height, observation_width) <= 0:
            raise ValueError("Episode length and image dimensions must be positive")
        if observation_width * 9 != observation_height * 16:
            raise ValueError("Preserve the selected full-frame 16:9 camera profile")
        if not np.isfinite([lift_height_m, hold_seconds]).all() or min(lift_height_m, hold_seconds) <= 0:
            raise ValueError("Lift height and hold duration must be positive and finite")
        self.contract = json.loads((HERE / "assets/robot-contract.json").read_text(encoding="utf-8"))
        for key in ("controlled_joints", "actuators", "action_limits_rad"):
            if len(self.contract[key]) != len(JOINT_NAMES):
                raise ValueError(f"{key} must describe seven independent actions")
        if self.contract["state_names"] != JOINT_NAMES or self.contract["action_names"] != JOINT_NAMES:
            raise ValueError("Contract names/order must match the declared LeRobot semantics")
        if self.contract["units"] != "rad" or self.contract["fps"] != FPS:
            raise ValueError("Contract units/rate differ from LeRobot metadata")
        self.scene = Path(scene) if scene is not None else HERE / "assets" / self.contract["scene_file"]
        self.reset_keyframe = reset_keyframe or self.contract["reset_keyframe"]
        self.task = "eb300_tool_lift"
        self.task_description = instruction
        self.fps = fps
        self._max_episode_steps = int(episode_length)
        self.height, self.width = int(observation_height), int(observation_width)
        self.lift_height_m, self.hold_seconds = float(lift_height_m), float(hold_seconds)
        self.render_shadows = bool(render_shadows)
        self.terminate_on_success = bool(terminate_on_success)
        limits = np.asarray(self.contract["action_limits_rad"], dtype=np.float32)
        if limits.shape != (7, 2) or not np.isfinite(limits).all() or np.any(limits[:, 0] >= limits[:, 1]):
            raise ValueError("action_limits_rad must contain seven finite ordered ranges")
        self.action_space = spaces.Box(limits[:, 0], limits[:, 1], dtype=np.float32)
        self.observation_space = spaces.Dict({
            "agent_pos": spaces.Box(-np.inf, np.inf, (7,), np.float32),
            "pixels": spaces.Dict({"wrist": spaces.Box(0, 255, (self.height, self.width, 3), np.uint8)}),
        })
        self.model: mujoco.MjModel | None = None
        self.data: mujoco.MjData | None = None
        self._renderer: mujoco.Renderer | None = None
        self._has_reset = False
        self._steps = 0
        self._held_s = 0.0
        self._done = False

    def _ensure_world(self) -> None:
        if self.model is not None:
            return
        model = mujoco.MjModel.from_xml_path(str(self.scene))
        if not np.isclose(model.opt.timestep, self.contract["physics_timestep_s"], atol=1e-12, rtol=0):
            raise ValueError("Scene timestep differs from the reviewed physics contract")
        qadr = np.array([model.joint(name).qposadr[0] for name in self.contract["controlled_joints"]])
        actuators = np.array([model.actuator(name).id for name in self.contract["actuators"]])
        if len(set(qadr.tolist())) != 7 or len(set(actuators.tolist())) != 7 or model.nu != 7:
            raise ValueError("Expected exactly seven distinct joint actuators, without diagnostic fixture")
        if not np.allclose(model.actuator_ctrlrange[actuators], np.stack((self.action_space.low, self.action_space.high), axis=1), atol=1e-6, rtol=0):
            raise ValueError("Contract limits differ from actual MJCF actuator ranges")
        for joint, actuator in zip(self.contract["controlled_joints"], actuators, strict=True):
            if model.jnt_type[model.joint(joint).id] != mujoco.mjtJoint.mjJNT_HINGE:
                raise ValueError(f"Controlled joint {joint} must use radians")
            if model.actuator_trnid[actuator, 0] != model.joint(joint).id:
                raise ValueError(f"Actuator does not target its declared joint {joint}")
        substeps = 1 / (self.fps * model.opt.timestep)
        if not np.isclose(substeps, round(substeps), atol=1e-8, rtol=0):
            raise ValueError("Control period must be an integer number of unchanged physics steps")
        body = model.body(self.contract["pencil_body"]).id
        joint = int(model.body_jntadr[body])
        if model.body_jntnum[body] != 1 or model.jnt_type[joint] != mujoco.mjtJoint.mjJNT_FREE:
            raise ValueError("Tool must have its own free joint")
        if model.body_mocapid[body] >= 0 or any(t != mujoco.mjtEq.mjEQ_JOINT for t in model.eq_type):
            raise ValueError("Only internal joint coupling is supported; tool attachments are forbidden")
        model.cam(self.contract["wrist_camera"])
        self._tool_body = body
        self._tool_geom = model.geom(self.contract["pencil_geom"]).id
        self._pads = {model.geom(name).id for name in self.contract["pad_geoms"]}
        if len(self._pads) != 2 or model.geom_bodyid[self._tool_geom] != body:
            raise ValueError("Expected two distinct pads and the tool's own contact geometry")
        self._qadr, self._actuators = qadr, actuators
        self._substeps = int(round(substeps))
        self.model, self.data = model, mujoco.MjData(model)

    def _observation(self) -> dict[str, Any]:
        return {"agent_pos": self.data.qpos[self._qadr].astype(np.float32), "pixels": {"wrist": self.render()}}

    def reset(self, seed: int | None = None, options: Mapping | None = None):
        super().reset(seed=seed)
        if options:
            raise ValueError("Reset options are not implemented; scene/keyframe is explicit")
        self._ensure_world()
        mujoco.mj_resetDataKeyframe(self.model, self.data, self.model.key(self.reset_keyframe).id)
        mujoco.mj_forward(self.model, self.data)
        self._has_reset = True
        self._initial_tool_z = float(self.data.xpos[self._tool_body, 2])
        self._steps, self._held_s, self._done = 0, 0.0, False
        self._max_pad_penetration = self._max_other_penetration = self._max_equality_residual = 0.0
        self._max_non_tool_penetration = self._max_force_cap_fraction = 0.0
        return self._observation(), {"is_success": False, "sim_time_s": float(self.data.time)}

    def _evaluate_physics_step(self) -> tuple[bool, dict[str, float]]:
        model, data = self.model, self.data
        contact_pads, other_contact = set(), False
        for i, contact in enumerate(data.contact[:data.ncon]):
            if self._tool_geom not in contact.geom:
                self._max_non_tool_penetration = max(self._max_non_tool_penetration, max(0.0, -float(contact.dist)))
                continue
            other = int(contact.geom[0] if contact.geom[1] == self._tool_geom else contact.geom[1])
            force = np.zeros(6)
            mujoco.mj_contactForce(model, data, i, force)
            penetration = max(0.0, -float(contact.dist))
            if other in self._pads:
                self._max_pad_penetration = max(self._max_pad_penetration, penetration)
                if force[0] > 0.005:
                    contact_pads.add(other)
            else:
                self._max_other_penetration = max(self._max_other_penetration, penetration)
                other_contact |= force[0] > 0.005
        eq = data.efc_pos[data.efc_type == mujoco.mjtConstraint.mjCNSTR_EQUALITY]
        self._max_equality_residual = max(self._max_equality_residual, float(np.max(np.abs(eq), initial=0)))
        force_caps = np.max(np.abs(model.actuator_forcerange[self._actuators]), axis=1)
        self._max_force_cap_fraction = max(self._max_force_cap_fraction,
                                          float(np.max(np.abs(data.actuator_force[self._actuators]) / force_caps)))
        lift = float(data.xpos[self._tool_body, 2]) - self._initial_tool_z
        holding = contact_pads == self._pads and not other_contact and lift >= self.lift_height_m
        self._held_s = self._held_s + model.opt.timestep if holding else 0.0
        metrics = {"lift_m": lift, "held_s": self._held_s,
                   "max_pad_penetration_m": self._max_pad_penetration,
                   "max_other_penetration_m": self._max_other_penetration,
                   "max_non_tool_penetration_m": self._max_non_tool_penetration,
                   "max_force_cap_fraction": self._max_force_cap_fraction,
                   "max_equality_residual": self._max_equality_residual}
        return self._held_s >= self.hold_seconds, metrics

    def step(self, action: np.ndarray):
        if not self._has_reset:
            raise RuntimeError("Call reset before step")
        if self._done:
            raise RuntimeError("Episode ended; call reset before another action")
        action = np.asarray(action, dtype=np.float64)
        if action.shape != (7,) or not np.isfinite(action).all():
            raise ValueError("Expected seven finite absolute joint targets in radians")
        clipped = np.clip(action, self.action_space.low, self.action_space.high)
        self.data.ctrl[self._actuators] = clipped
        success = False
        for _ in range(self._substeps):
            previous_time = self.data.time
            mujoco.mj_step(self.model, self.data)
            if (not np.isfinite(self.data.qpos).all() or not np.isfinite(self.data.qvel).all()
                or not np.isclose(self.data.time - previous_time, self.model.opt.timestep, atol=1e-10, rtol=0)
                or any(w.number for w in self.data.warning)):
                raise RuntimeError("MuJoCo warning, nonfinite state or time reset; rollout rejected")
            current_success, metrics = self._evaluate_physics_step()
            success |= current_success
        self._steps += 1
        truncated = self._steps >= self._max_episode_steps
        terminated = bool(success and self.terminate_on_success)
        self._done = bool(terminated or truncated)
        info = {"is_success": bool(success), "metrics": metrics, "sim_time_s": float(self.data.time),
                "action_clipped": bool(np.any(action != clipped))}
        return self._observation(), float(success), terminated, bool(truncated), info

    def render(self, camera: str | None = None) -> np.ndarray:
        if not self._has_reset:
            raise RuntimeError("Call reset before render")
        if camera not in (None, "wrist", self.contract["wrist_camera"]):
            raise ValueError("Only the full wrist image is an environment sensor")
        self._ensure_world()
        if self._renderer is None:
            self._renderer = mujoco.Renderer(self.model, self.height, self.width)
        self._renderer.update_scene(self.data, camera=self.contract["wrist_camera"])
        self._renderer.scene.flags[mujoco.mjtRndFlag.mjRND_SHADOW] = self.render_shadows
        return self._renderer.render().copy()

    def close(self) -> None:
        if self._renderer is not None:
            self._renderer.close()
            self._renderer = None
        self.model = self.data = None
        self._has_reset = False


def make_env(n_envs: int = 1, use_async_envs: bool = False, **kwargs: Any):
    """Unmodified EnvHub factory convention; LeRobot supplies its own runner."""
    if n_envs < 1:
        raise ValueError("n_envs must be positive")
    factory = partial(EB300Env, **kwargs)
    vector_cls = gym.vector.AsyncVectorEnv if use_async_envs else gym.vector.SyncVectorEnv
    return {"eb300_tool_lift": {0: vector_cls([factory] * n_envs)}}
