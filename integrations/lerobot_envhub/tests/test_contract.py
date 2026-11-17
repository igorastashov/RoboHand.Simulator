"""Run with local geometry restored: python -m unittest discover -s tests -v."""

import importlib.util
from pathlib import Path
import unittest

import numpy as np

MODULE_PATH = Path(__file__).resolve().parents[1] / "env.py"
SPEC = importlib.util.spec_from_file_location("eb300_env_test", MODULE_PATH)
ENV = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ENV)


class EB300ContractTests(unittest.TestCase):
    def setUp(self):
        self.env = ENV.EB300Env(observation_height=90, observation_width=160, episode_length=40)
        self.obs, _ = self.env.reset(seed=17)

    def tearDown(self):
        self.env.close()

    def test_one_camera_seven_radian_actions_and_time(self):
        self.assertEqual(list(self.obs["pixels"]), ["wrist"])
        self.assertEqual(self.obs["pixels"]["wrist"].shape, (90, 160, 3))
        self.assertEqual(self.obs["pixels"]["wrist"].dtype, np.uint8)
        self.assertEqual(self.obs["agent_pos"].shape, (7,))
        self.assertTrue(self.env.observation_space.contains(self.obs))
        initial = self.env.data.ctrl[self.env._actuators].copy()
        for _ in range(10):
            obs, reward, ended, truncated, info = self.env.step(initial)
            self.assertTrue(np.isfinite(obs["agent_pos"]).all())
            self.assertFalse(info["is_success"])
            self.assertEqual(reward, 0)
            self.assertFalse(ended or truncated)
        self.assertAlmostEqual(info["sim_time_s"], 10 / 25, places=9)
        self.assertAlmostEqual(self.env.model.opt.timestep, .002, places=12)

    def test_bad_actions_do_not_advance_physics(self):
        for bad in (np.zeros(6), np.zeros(8), np.full(7, np.nan), np.full(7, np.inf)):
            before = self.env.data.time
            with self.assertRaises(ValueError):
                self.env.step(bad)
            self.assertEqual(self.env.data.time, before)
        with self.assertRaises(ValueError):
            self.env.render("overview")

    def test_reset_and_episode_end(self):
        initial = self.obs["agent_pos"].copy()
        image = self.obs["pixels"]["wrist"].copy()
        self.env.step(self.env.data.ctrl[self.env._actuators].copy())
        again, _ = self.env.reset(seed=17)
        np.testing.assert_array_equal(initial, again["agent_pos"])
        np.testing.assert_array_equal(image, again["pixels"]["wrist"])
        self.env._max_episode_steps = 1
        _, _, _, truncated, _ = self.env.step(self.env.data.ctrl[self.env._actuators].copy())
        self.assertTrue(truncated)
        with self.assertRaises(RuntimeError):
            self.env.step(initial)

    def test_evaluator_rejects_lift_without_pad_contact(self):
        joint = self.env.model.body_jntadr[self.env._tool_body]
        qadr = self.env.model.jnt_qposadr[joint]
        self.env.data.qpos[qadr:qadr+3] = (2., 2., 2.)
        ENV.mujoco.mj_forward(self.env.model, self.env.data)
        for _ in range(300):
            success, metrics = self.env._evaluate_physics_step()
        self.assertGreater(metrics["lift_m"], self.env.lift_height_m)
        self.assertFalse(success)
        self.assertEqual(metrics["held_s"], 0)

    def test_rate_and_aspect_are_not_silently_changed(self):
        with self.assertRaises(ValueError):
            ENV.EB300Env(fps=30)
        with self.assertRaises(ValueError):
            ENV.EB300Env(observation_height=480, observation_width=640)

    def test_unreset_environment_cannot_render_or_advance(self):
        fresh = ENV.EB300Env(observation_height=90, observation_width=160)
        try:
            with self.assertRaises(RuntimeError):
                fresh.render()
            with self.assertRaises(RuntimeError):
                fresh.step(np.zeros(7))
        finally:
            fresh.close()


if __name__ == "__main__":
    unittest.main()
