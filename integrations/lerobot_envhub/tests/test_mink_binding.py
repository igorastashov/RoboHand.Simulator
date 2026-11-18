"""Meaningful regression checks for the separately approved Mink binding."""

from pathlib import Path
import sys
import unittest

import mujoco
import numpy as np

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
from env import EB300Env
from teleop_mink import MinkBinding, TargetRejected, sync_viewer


class MinkBindingTests(unittest.TestCase):
    def setUp(self):
        self.env = EB300Env(scene=HERE / "assets/eb300_mink_teleop.xml", observation_width=160,
                            observation_height=90, episode_length=150, render_shadows=False)
        self.env.reset(seed=17)
        self.binding = MinkBinding(self.env)

    def tearDown(self):
        self.env.close()

    def test_nonphysical_marker_does_not_change_dynamics_or_sensor(self):
        base = EB300Env(observation_width=160, observation_height=90, render_shadows=False)
        try:
            base.reset(seed=17)
            marker = self.env.model.geom("eb300/teleop_target_marker")
            self.assertEqual(marker.contype[0], 0)
            self.assertEqual(marker.conaffinity[0], 0)
            self.assertEqual(marker.group[0], 5)
            camera = self.env.model.camera(self.env.contract["wrist_camera"]).id
            # Put the marker directly in front of the sensor: invisibility must
            # follow from rendering groups, not from it happening to be offscreen.
            R = self.env.data.cam_xmat[camera].reshape(3, 3)
            self.env.data.mocap_pos[0] = self.env.data.cam_xpos[camera] - .1 * R[:, 2]
            mujoco.mj_forward(self.env.model, self.env.data)
            np.testing.assert_array_equal(self.env.render(), base.render())
            action = base.data.ctrl.copy()
            for _ in range(4):
                b, *_ = base.step(action)
                t, *_ = self.env.step(action)
                np.testing.assert_allclose(self.env.data.qpos, base.data.qpos, atol=1e-12, rtol=0)
                np.testing.assert_array_equal(t["pixels"]["wrist"], b["pixels"]["wrist"])
        finally:
            base.close()

    def test_no_input_holds_existing_targets_despite_measured_pd_sag(self):
        original = self.env.data.ctrl.copy()
        self.assertGreater(abs(self.env.data.qpos[1] - original[1]), .02)
        for _ in range(5):
            action = self.binding.action(float(original[6]))
            np.testing.assert_allclose(action, original, atol=1e-7, rtol=0)
            self.env.step(action)

    def test_invalid_and_unreachable_targets_cannot_edit_physical_world(self):
        before_q, before_ctrl, before_time = self.env.data.qpos.copy(), self.env.data.ctrl.copy(), self.env.data.time
        accepted = self.binding.target.copy()
        far = accepted.copy()
        far[:3, 3] = [1.4, 1.4, 1.9]  # inside declared box, beyond chain reach
        bad_rotation = accepted.copy()
        bad_rotation[0, 0] += .2
        for bad in (np.zeros(3), np.full((4, 4), np.nan), bad_rotation, far):
            with self.assertRaises(TargetRejected):
                self.binding.set_target(bad)
            np.testing.assert_array_equal(self.binding.target, accepted)
            np.testing.assert_array_equal(self.env.data.qpos, before_q)
            np.testing.assert_array_equal(self.env.data.ctrl, before_ctrl)
            self.assertEqual(self.env.data.time, before_time)
        with self.assertRaises(ValueError):
            self.binding.action(float("nan"))

    def test_pose_and_gripper_commands_use_only_seven_bounded_radian_actions(self):
        target = self.binding.target.copy()
        target[0, 3] += .004
        self.binding.set_target(target)
        initial_free = self.env.data.qpos[10:].copy()
        last = self.binding.last_action.copy()
        for _ in range(12):
            physical_before = self.env.data.qpos.copy()
            action = self.binding.action(.6)
            self.assertEqual(action.shape, (7,))
            self.assertTrue(np.isfinite(action).all())
            self.assertLessEqual(np.max(np.abs(action[:6] - last[:6])), .35 / 25 + 2e-7)
            self.assertLessEqual(abs(float(action[6]) - last[6]), .6 / 25 + 2e-7)
            np.testing.assert_array_equal(self.env.data.qpos, physical_before)
            self.env.step(action)
            last = action
        self.assertLess(self.env.data.qpos[6], .95)
        # Only the physical engine settles the pencil on the table; IK never
        # transports it with the gripper or changes its orientation.
        np.testing.assert_allclose(self.env.data.qpos[10:12], initial_free[:2], atol=1e-7, rtol=0)
        np.testing.assert_allclose(self.env.data.qpos[13:], initial_free[3:], atol=1e-7, rtol=0)
        self.assertLess(abs(float(self.env.data.qpos[12] - initial_free[2])), .0002)

    def test_explicit_continue_mode_preserves_success_event_and_allows_next_step(self):
        # Lifecycle unit check only: this override is not physical grasp evidence.
        self.env.terminate_on_success = False
        self.env._evaluate_physics_step = lambda: (True, {"unit_lifecycle_only": 1.})
        action = self.env.data.ctrl.copy()
        _, reward, terminated, truncated, info = self.env.step(action)
        self.assertEqual(reward, 1.)
        self.assertTrue(info["is_success"])
        self.assertFalse(terminated or truncated)
        self.env._evaluate_physics_step = lambda: (False, {"unit_lifecycle_only": 1.})
        _, reward, terminated, _, info = self.env.step(action)
        self.assertEqual(reward, 0.)
        self.assertFalse(info["is_success"] or terminated)
        self.env.terminate_on_success = True
        self.env._evaluate_physics_step = lambda: (True, {"unit_lifecycle_only": 1.})
        self.assertTrue(self.env.step(action)[2])
        with self.assertRaises(RuntimeError):
            self.env.step(action)

    def test_generic_viewer_cannot_assist_object_motion_or_change_gravity(self):
        class Viewer:
            def __init__(self, edit):
                self.edit = edit
            def sync(self):
                self.edit()
        # A view-only/mocap update is allowed.
        sync_viewer(Viewer(lambda: None), self.env)
        with self.assertRaises(RuntimeError):
            sync_viewer(Viewer(lambda: self.env.data.xfrc_applied.__setitem__((self.env._tool_body, 0), 1.)), self.env)
        self.env.data.xfrc_applied[:] = 0.
        with self.assertRaises(RuntimeError):
            sync_viewer(Viewer(lambda: self.env.model.opt.gravity.__setitem__(2, 0.)), self.env)


if __name__ == "__main__":
    unittest.main()
