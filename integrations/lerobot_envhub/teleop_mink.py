# Copyright 2026 RoboHand contributors. SPDX-License-Identifier: Apache-2.0
"""Approved EB300 binding: upstream Mink/TeleopMocap, MuJoCo viewer, LeRobot writer.

No new IK solver, motor law, planner, GUI or recording format. Fixed headless
targets are diagnostic operator inputs, never a learned or autonomous policy.
"""

import argparse
from contextlib import nullcontext
import json
from pathlib import Path
from queue import Empty, SimpleQueue
import time

import mink
import mujoco
import numpy as np

from env import EB300Env, FPS, HERE, JOINT_NAMES


class TargetRejected(ValueError):
    """Invalid or unachievable nominal target; previous commands stay unchanged."""


class MinkBinding:
    def __init__(self, env: EB300Env, config: dict | None = None):
        if not env._has_reset:
            raise RuntimeError("Reset the physical environment first")
        self.env, self.model = env, env.model
        self.config = config or json.loads((HERE / "mink-config.json").read_text(encoding="utf-8"))
        self.dt = 1 / FPS
        self.arm_qadr = env._qadr[:6]
        if not np.array_equal(self.arm_qadr, np.arange(6)):
            raise ValueError("This reviewed scene has the six arm coordinates first")
        self.arm_dofs = np.array([self.model.joint(n).dofadr[0] for n in env.contract["controlled_joints"][:6]])
        if len(set(self.arm_dofs.tolist())) != 6:
            raise ValueError("Expected six separate arm hinges")
        self.frozen_dofs = [i for i in range(self.model.nv) if i not in self.arm_dofs]
        self.freeze = mink.DofFreezingTask(self.model, self.frozen_dofs)
        self.configuration = mink.Configuration(self.model, q=env.data.qpos.copy())
        # Upstream actuator example integrates a commanded configuration. Preserve
        # the existing position targets at connect; do not repeatedly turn PD sag
        # into a new target or add a hidden gravity-compensation controller.
        q = self.configuration.q.copy()
        q[self.arm_qadr] = env.data.ctrl[env._actuators[:6]]
        self.configuration.update(q)
        self.task = mink.FrameTask(self.config["frame_body"], "body", position_cost=1., orientation_cost=1., lm_damping=1e-5)
        moving = [g for g in mink.get_subtree_geom_ids(self.model, self.model.body(self.config["moving_root_body"]).id)
                  if self.model.geom_contype[g] or self.model.geom_conaffinity[g]]
        obstacles = [g for g in range(self.model.ngeom) if g not in moving and g != env._tool_geom
                     and (self.model.geom_contype[g] or self.model.geom_conaffinity[g])]
        self.limits = [mink.ConfigurationLimit(self.model),
                       mink.VelocityLimit(self.model, {n: self.config["arm_velocity_limit_rad_s"] for n in env.contract["controlled_joints"][:6]}),
                       mink.CollisionAvoidanceLimit(self.model, [(moving, obstacles)],
                           minimum_distance_from_collisions=self.config["collision_min_distance_m"],
                           collision_detection_distance=self.config["collision_detection_distance_m"])]
        self.target = self.configuration.get_transform_frame_to_world(self.config["frame_body"], "body").as_matrix()
        self.task.set_target(mink.SE3.from_matrix(self.target))
        self.last_action = env.data.ctrl[env._actuators].copy()

    def _configuration_at_commands(self) -> np.ndarray:
        q = self.env.data.qpos.copy()
        q[self.arm_qadr] = self.configuration.q[self.arm_qadr]
        return q

    def set_target(self, target: np.ndarray) -> None:
        target = np.asarray(target, dtype=float)
        if target.shape != (4, 4) or not np.isfinite(target).all():
            raise TargetRejected("Expected a finite4x4 world-from-C transform")
        R = target[:3, :3]
        if (not np.allclose(target[3], [0, 0, 0, 1], atol=1e-9)
                or not np.allclose(R.T @ R, np.eye(3), atol=1e-7)
                or not np.isclose(np.linalg.det(R), 1., atol=1e-7)):
            raise TargetRejected("Target must be a rigid transform")
        if np.any(target[:3, 3] < self.config["workspace_world_min_m"]) or np.any(target[:3, 3] > self.config["workspace_world_max_m"]):
            raise TargetRejected("Target outside the declared diagnostic workspace")
        if np.allclose(target, self.target, rtol=0, atol=1e-10):
            return
        # Validate on a separate configuration; this never advances or edits the
        # physical world, its object poses, commands, or the accepted goal.
        preview = mink.Configuration(self.model, q=self._configuration_at_commands())
        task = mink.FrameTask(self.config["frame_body"], "body", position_cost=1., orientation_cost=1., lm_damping=1e-5)
        task.set_target(mink.SE3.from_matrix(target))
        try:
            for _ in range(self.config["preview_iterations"]):
                velocity = mink.solve_ik(preview, [task], self.dt, "daqp", limits=self.limits, constraints=[self.freeze], damping=1e-6)
                preview.integrate_inplace(velocity, self.dt)
                error = task.compute_error(preview)
                if (np.linalg.norm(error[:3]) <= self.config["preview_position_tolerance_m"]
                        and np.linalg.norm(error[3:]) <= self.config["preview_orientation_tolerance_rad"]):
                    break
            else:
                raise TargetRejected(f"Nominal IK did not converge: position={np.linalg.norm(error[:3]):.6g}m, orientation={np.linalg.norm(error[3:]):.6g}rad")
        except TargetRejected:
            raise
        except Exception as exc:
            raise TargetRejected(f"Upstream IK rejected the target: {exc}") from exc
        self.target = target.copy()
        self.task.set_target(mink.SE3.from_matrix(self.target))

    def action(self, gripper_rad: float) -> np.ndarray:
        if not np.isfinite(gripper_rad) or not self.env.action_space.low[6] <= gripper_rad <= self.env.action_space.high[6]:
            raise ValueError("Gripper command must be a finite in-range angle in radians")
        q_before = self._configuration_at_commands()
        self.configuration.update(q_before)
        velocity = mink.solve_ik(self.configuration, [self.task], self.dt, "daqp", limits=self.limits, constraints=[self.freeze], damping=1e-6)
        self.configuration.integrate_inplace(velocity, self.dt)
        if not np.allclose(self.configuration.q[6:], q_before[6:], rtol=0, atol=1e-10):
            raise RuntimeError("IK changed a non-arm coordinate")
        action = self.last_action.copy()
        action[:6] = self.configuration.q[self.arm_qadr]
        step = self.config["gripper_velocity_limit_rad_s"] * self.dt
        action[6] += np.clip(gripper_rad - action[6], -step, step)
        if not np.isfinite(action).all() or np.any(action < self.env.action_space.low - 1e-6) or np.any(action > self.env.action_space.high + 1e-6):
            raise RuntimeError("IK action violates the physical action contract")
        self.last_action = action.copy()
        return action.astype(np.float32)


def create_dataset(root: Path):
    from lerobot.datasets import LeRobotDataset
    features = {
        "observation.state": {"dtype": "float32", "shape": (7,), "names": JOINT_NAMES},
        "action": {"dtype": "float32", "shape": (7,), "names": JOINT_NAMES},
        "observation.images.wrist": {"dtype": "image", "shape": (360, 640, 3), "names": ["height", "width", "channels"]},
    }
    return LeRobotDataset.create("local/eb300-mink-teleop", fps=FPS, features=features, root=root,
                                robot_type="eb300", use_videos=False, image_writer_threads=2)


def sync_viewer(viewer, env):
    """Allow camera/mocap input, reject native GUI physics edits or body forces.

    MuJoCo's generic viewer also exposes perturbations and physics controls;
    assisted/edited dynamics must never become an accepted demonstration.
    """
    data_names = ("qpos", "qvel", "act", "ctrl", "eq_active")
    model_names = ("body_mass", "body_inertia", "actuator_gainprm", "actuator_biasprm", "actuator_forcerange")
    before_data = {name: getattr(env.data, name).copy() for name in data_names}
    before_model = {name: getattr(env.model, name).copy() for name in model_names}
    before_time = env.data.time
    before_gravity = env.model.opt.gravity.copy()
    before_options = (env.model.opt.timestep, env.model.opt.disableflags, env.model.opt.enableflags)
    viewer.sync()
    if (any(not np.array_equal(getattr(env.data, n), v) for n, v in before_data.items())
            or any(not np.array_equal(getattr(env.model, n), v) for n, v in before_model.items())
            or env.data.time != before_time or np.any(env.data.qfrc_applied) or np.any(env.data.xfrc_applied)
            or not np.array_equal(env.model.opt.gravity, before_gravity)
            or before_options != (env.model.opt.timestep, env.model.opt.disableflags, env.model.opt.enableflags)):
        raise RuntimeError("Viewer changed physical state/options or applied external forces; recording rejected")


def run(args):
    if args.steps < 1:
        raise ValueError("steps must be positive")
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=False)
    instruction_kwargs = {"instruction": args.instruction} if args.instruction else {}
    env = EB300Env(scene=args.scene, episode_length=args.steps, render_shadows=not args.no_shadows,
                   terminate_on_success=not args.continue_after_success, **instruction_kwargs)
    dataset = None
    rows, failure, success = [], None, False
    try:
        observation, _ = env.reset(seed=17)
        binding = MinkBinding(env)
        stages = json.loads(Path(args.targets).read_text(encoding="utf-8")) if args.targets else []
        if stages and (not args.headless or not all(isinstance(s.get("steps"), int) and s["steps"] > 0 for s in stages)):
            raise ValueError("Fixed target inputs require headless mode and positive integer stage lengths")
        if args.record:
            dataset = create_dataset(output / "dataset")
        target_id = env.model.body(binding.config["target_body"]).mocapid[0]
        if target_id < 0 or env.model.nmocap != 1:
            raise ValueError("Use the reviewed teleop scene with its single nonphysical target")
        keys = SimpleQueue()
        from mink.contrib import TeleopMocap
        keyboard = TeleopMocap(env.data)
        env.data.mocap_pos[target_id] = binding.target[:3, 3]
        mujoco.mju_mat2Quat(env.data.mocap_quat[target_id], binding.target[:3, :3].reshape(9))
        viewer_context = nullcontext(None)
        if not args.headless:
            from mujoco import viewer as mjviewer
            viewer_context = mjviewer.launch_passive(env.model, env.data, key_callback=keys.put)
            print("Mink:9 enable, arrows/6/7 local XYZ, . rotate, +/- step. [ close, ] open. Close viewer to finish.")
        gripper, stage_index, stage_left = float(binding.last_action[6]), 0, 0
        with viewer_context as viewer:
            if viewer is not None:
                with viewer.lock():
                    viewer.opt.geomgroup[5] = 1
                    viewer.cam.type = mujoco.mjtCamera.mjCAMERA_FIXED
                    viewer.cam.fixedcamid = env.model.camera("overview").id
            for tick in range(args.steps):
                started = time.perf_counter()
                if viewer is not None and not viewer.is_running():
                    break
                if stages and stage_left == 0:
                    if stage_index == len(stages):
                        break
                    stage = stages[stage_index]
                    binding.set_target(np.asarray(stage["T_world_C"]))
                    gripper = float(stage["gripper_rad"])
                    stage_left, stage_index = stage["steps"], stage_index + 1
                if viewer is not None:
                    with viewer.lock():
                        while not keys.empty():
                            try:
                                key = keys.get_nowait()
                            except Empty:
                                break
                            if key == ord("["):
                                gripper = binding.config["close_angle_rad"]
                            elif key == ord("]"):
                                gripper = binding.config["open_angle_rad"]
                            else:
                                keyboard(key)
                        keyboard.auto_key_move()
                        target = mink.SE3.from_mocap_name(env.model, env.data, binding.config["target_body"]).as_matrix()
                    try:
                        binding.set_target(target)
                    except TargetRejected as exc:
                        print(f"Target rejected; previous goal retained: {exc}")
                        env.data.mocap_pos[target_id] = binding.target[:3, 3]
                        mujoco.mju_mat2Quat(env.data.mocap_quat[target_id], binding.target[:3, :3].reshape(9))
                action = binding.action(gripper)
                before = observation
                observation, _, ended, truncated, info = env.step(action)
                if dataset is not None:
                    dataset.add_frame({"observation.state": before["agent_pos"], "observation.images.wrist": before["pixels"]["wrist"],
                                       "action": action, "task": env.task_description})
                contacts = [{"geoms": [env.model.geom(int(g)).name for g in c.geom], "depth_m": -float(c.dist)}
                            for c in env.data.contact[:env.data.ncon] if c.dist < -.002]
                tool_contacts = []
                for ci, contact in enumerate(env.data.contact[:env.data.ncon]):
                    if env._tool_geom in contact.geom:
                        force = np.zeros(6)
                        mujoco.mj_contactForce(env.model, env.data, ci, force)
                        tool_contacts.append({"geoms": [env.model.geom(int(g)).name for g in contact.geom],
                                              "signed_distance_m": float(contact.dist), "normal_force_N": float(force[0])})
                rows.append({"tick": tick, "action_rad": action.tolist(), "post_state_rad": observation["agent_pos"].tolist(),
                             "target_world_C": binding.target.tolist(), "actual_C_xyz_m": env.data.body(binding.config["frame_body"]).xpos.tolist(),
                             "pencil_xyz_m": env.data.xpos[env._tool_body].tolist(), "info": info,
                             "tool_contacts": tool_contacts, "actuator_force_Nm": env.data.actuator_force[env._actuators].tolist(),
                             "contacts_deeper_than_2mm": contacts, "wall_work_s": time.perf_counter() - started})
                success |= info["is_success"]
                if contacts:
                    raise RuntimeError("Deep physical contact; diagnostic stopped")
                if viewer is not None:
                    sync_viewer(viewer, env)
                    time.sleep(max(0., 1 / FPS - (time.perf_counter() - started)))
                if stages:
                    stage_left -= 1
                if ended or truncated:
                    break
    except Exception as exc:
        failure = f"{type(exc).__name__}: {exc}"
        raise
    finally:
        if dataset is not None:
            try:
                if rows:
                    dataset.save_episode()
            finally:
                dataset.finalize()
        report = {"mode": "fixed diagnostic targets" if args.headless else "human teleoperation", "learned_policy": False,
                  "task_success": bool(success and failure is None), "failure": failure, "frames": len(rows), "fps": FPS,
                  "single_full_wrist_shape": [360, 640, 3], "render_shadows": not args.no_shadows, "rows": rows}
        report["continued_after_success"] = args.continue_after_success
        (output / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        env.close()
        print(json.dumps({k: v for k, v in report.items() if k != "rows"}), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scene", type=Path, default=HERE / "assets/eb300_mink_teleop.xml")
    parser.add_argument("--output", required=True)
    parser.add_argument("--steps", type=int, default=2500)
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--targets", help="JSON list of fixed operator target matrices/gripper angles/step counts; no planner")
    parser.add_argument("--record", action="store_true", help="Use stock LeRobotDataset writer; never uploads")
    parser.add_argument("--instruction", help="Literal task annotation for the demonstration; match the whole recorded episode")
    parser.add_argument("--no-shadows", action="store_true")
    parser.add_argument("--continue-after-success", action="store_true", help="Explicitly keep the episode open for lowering/release; default evaluator termination is unchanged")
    run(parser.parse_args())
