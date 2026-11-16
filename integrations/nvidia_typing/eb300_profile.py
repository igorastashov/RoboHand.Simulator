"""EB300 configuration for the existing pinned NVIDIA teacher/vision environment.

Owner-approved 2026-11-16. Uses Isaac Lab's existing articulation, implicit
actuator, rate action, camera, command, reset and PPO components. Dynamics and
optics are nominal simulation settings, not measured hardware calibration.
The first training scene uses robot-base coordinates; desktop placement is a
separate world transform and is not inferred by this configuration.
"""

import math
import os
from pathlib import Path


JOINTS = tuple(f"J{i}" for i in range(1, 7))
REST = (-0.785398163, 0.90, 0.85, 0.0, -0.7, 1.0)


def configure_eb300(cfg):
    """Apply standard framework configuration before environment construction."""
    import isaaclab.sim as sim_utils
    from isaaclab.actuators import ImplicitActuatorCfg
    from isaaclab.assets import ArticulationCfg
    from isaaclab.managers import SceneEntityCfg
    from isaaclab.sensors import CameraCfg
    from isaaclab_ov.renderers import OVRTXRendererCfg

    usd = Path(os.environ.get(
        "EB300_USD", "/eb300/usd-robot-ascii/eb300_welded_contacts.usda"
    ))
    if not usd.is_file():
        raise FileNotFoundError(f"Mount the owner's EB300 USD asset: {usd}")
    cfg.scene.robot = ArticulationCfg(
        prim_path="{ENV_REGEX_NS}/Robot",
        articulation_root_prim_path="/Geometry/base_footprint",
        spawn=sim_utils.UsdFileCfg(
            usd_path=str(usd), copy_from_source=False,
            activate_contact_sensors=True,
            articulation_props=sim_utils.ArticulationRootPropertiesCfg(
                enabled_self_collisions=True
            ),
        ),
        init_state=ArticulationCfg.InitialStateCfg(
            pos=(0.0, 0.0, 0.0), rot=(0.0, 0.0, 0.0, 1.0),
            joint_pos=dict(zip(JOINTS, REST)), joint_vel={".*": 0.0},
        ),
        soft_joint_pos_limit_factor=1.0,
        actuators={"arm": ImplicitActuatorCfg(
            joint_names_expr=list(JOINTS),
            stiffness=dict(zip(JOINTS, (500., 900., 650., 220., 180., 130.))),
            damping=dict(zip(JOINTS, (30., 55., 40., 12., 10., 8.))),
            armature={".*": 0.02},
            effort_limit_sim=dict(zip(JOINTS, (40., 35., 25., 12., 10., 8.))),
            velocity_limit_sim={".*": 0.3},
        )},
    )
    action = cfg.actions.action
    action.joint_names = JOINTS
    action.q_reset_ref = REST
    action.velocity_limits_rad_s = (0.15, 0.15, 0.15, 0.20, 0.20, 0.20)
    command = cfg.commands.typing
    command.controlled_joint_names = JOINTS
    command.q_reset_ref = REST
    command.tip_body = "wrist3_link"
    command.tip_offset_m = (0.0159297, -0.137, -0.00770394)
    command.reset.enabled = False
    # Existing scrape reward/termination must use the same physical jaw TCP.
    for group in (cfg.rewards, cfg.terminations):
        for term in vars(group).values():
            params = getattr(term, "params", None)
            if isinstance(params, dict) and "tip_body" in params:
                params["tip_body"] = command.tip_body
                params["tip_offset"] = command.tip_offset_m
    cfg.events.reset_robot_rest.params["asset_cfg"] = SceneEntityCfg(
        "robot", joint_names=list(JOINTS)
    )
    # The accepted R8 gripper opening is rigid, not a seventh actuated joint.
    cfg.events.reset_gripper_closed = None
    cfg.scene.robot_contact.prim_path = "{ENV_REGEX_NS}/Robot/Geometry/.*"

    optical_frame = (
        "/Geometry/base_footprint/base_link/shoulder_link/upper_arm_link/"
        "forearm_link/wrist1_link/wrist2_link/wrist3_link/phone_link/"
        "camera_optical_frame/RedmiCamera"
    )
    # CAD optical +Z-forward becomes OpenGL -Z-forward by a 180-degree X turn.
    # This runtime's quaternions are xyzw, as verified from CameraCfg source.
    aperture = 20.955
    focal = (aperture * 120 / 160) / (2 * math.tan(math.radians(60) / 2))
    cfg.scene.camera_wrist = CameraCfg(
        prim_path="{ENV_REGEX_NS}/Robot" + optical_frame,
        offset=CameraCfg.OffsetCfg(rot=(1., 0., 0., 0.), convention="opengl"),
        update_period=.04, height=120, width=160, data_types=["rgb"],
        update_latest_camera_pose=True,
        spawn=sim_utils.PinholeCameraCfg(
            focal_length=focal, horizontal_aperture=aperture,
            clipping_range=(.01, 10.),
        ),
        renderer_cfg=OVRTXRendererCfg(log_level="warn"),
    )
    cfg.task_contract = "EB300_R8_6DOF_nominal_PPO_teacher_vision_v1"
    print("EB300 PROFILE: six arm actions, nominal dynamics, wrist Redmi camera", flush=True)
    return cfg
