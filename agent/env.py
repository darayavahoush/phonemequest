"""
Gymnasium environment wrapping the student simulator, so both the tabular/
bandit baselines and a future PPO agent can be trained against the same
interface. See the project doc, Section 3.5, for the baseline ladder this
supports: rule-based -> contextual bandit -> tabular Q -> deep policy.

Reward is currently the simple "target success-rate zone" version. Swap in
Absolute Learning Progress (Section 3.6 of the doc) once you're ready for
the stronger version — the hook is marked below.
"""

import numpy as np
import gymnasium as gym
from gymnasium import spaces

from simulator.student_model import make_random_child

TARGET_SUCCESS_RATE = 0.75
WINDOW = 5


class DifficultyEnv(gym.Env):
    def __init__(self, episode_length: int = 50, calibrated_ranges=None):
        super().__init__()
        self.episode_length = episode_length
        self.calibrated_ranges = calibrated_ranges  # None = original hand-picked defaults
        # state: [recent success rate, current difficulty, frustration proxy]
        self.observation_space = spaces.Box(low=0.0, high=1.0, shape=(3,), dtype=np.float32)
        # actions: lower difficulty, hold, raise difficulty
        self.action_space = spaces.Discrete(3)
        self.child = None
        self.difficulty = 0.5
        self.recent = []
        self.step_count = 0

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.child = make_random_child(self.calibrated_ranges)
        self.difficulty = 0.5
        self.recent = []
        self.step_count = 0
        return self._obs(), {}

    def step(self, action):
        self.difficulty = float(np.clip(self.difficulty + [-0.05, 0.0, 0.05][action], 0.0, 1.0))
        record = self.child.attempt(self.difficulty)
        self.recent.append(record["success"])
        self.recent = self.recent[-WINDOW:]

        # TODO: replace with Absolute Learning Progress reward (doc Section 3.6) —
        # reward magnitude of change in skill_level rather than distance from a
        # fixed target success rate.
        success_rate = float(np.mean(self.recent)) if self.recent else 0.0
        reward = 1.0 - abs(success_rate - TARGET_SUCCESS_RATE)
        reward -= record["frustration"] * 0.5
        if record["quit"]:
            reward -= 1.0

        self.step_count += 1
        terminated = record["quit"]
        truncated = self.step_count >= self.episode_length
        return self._obs(), reward, terminated, truncated, {}

    def _obs(self):
        success_rate = float(np.mean(self.recent)) if self.recent else 0.5
        return np.array([success_rate, self.difficulty, self.child.frustration], dtype=np.float32)
