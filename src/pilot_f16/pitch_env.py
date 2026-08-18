"""M01.2 pitch-stabilization environment."""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import gymnasium as gym
import jsbsim
import numpy as np


class F16PitchEnv(gym.Env[np.ndarray, np.ndarray]):
    """Pitch-only lesson with roll, yaw and throttle held by a trim teacher."""

    metadata = {"render_modes": []}
    physics_hz = 120
    policy_hz = 20
    action_repeat = physics_hz // policy_hz

    def __init__(self, episode_seconds: float = 30.0, output_directive: Path | None = None) -> None:
        super().__init__()
        self.episode_seconds = episode_seconds
        self.output_directive = output_directive
        self.action_space = gym.spaces.Box(-1.0, 1.0, shape=(1,), dtype=np.float32)
        self.observation_space = gym.spaces.Box(-np.inf, np.inf, shape=(16,), dtype=np.float32)
        self._fdm: jsbsim.FGFDMExec | None = None
        self._steps = 0
        self._target_pitch_rad = 0.0
        self._previous_action = np.zeros(1, dtype=np.float32)
        self._teacher_aileron = 0.0
        self._teacher_rudder = 0.0
        self._teacher_throttle = 0.0

    def _new_fdm(self) -> jsbsim.FGFDMExec:
        fdm = jsbsim.FGFDMExec(None)
        fdm.set_debug_level(0)
        fdm.set_dt(1.0 / self.physics_hz)
        if not fdm.load_model("f16"):
            raise RuntimeError("Bundled JSBSim f16 baseline could not be loaded")
        if self.output_directive is not None:
            fdm.set_output_directive(str(self.output_directive.resolve()))
            fdm.enable_output()
        return fdm

    def reset(self, *, seed: int | None = None, options: dict[str, Any] | None = None):
        super().reset(seed=seed)
        options = options or {}
        self._fdm = self._new_fdm()
        fdm = self._fdm
        initial = {
            "ic/h-sl-ft": float(options.get("altitude_ft", 15_000.0)),
            "ic/vc-kts": float(options.get("airspeed_kts", 350.0)),
            "ic/phi-deg": 0.0,
            "ic/theta-deg": 0.0,
            "ic/psi-true-deg": float(options.get("heading_deg", 0.0)),
            "ic/gamma-deg": 0.0,
        }
        for prop, value in initial.items():
            fdm[prop] = value
        if not fdm.run_ic():
            raise RuntimeError("JSBSim run_ic() failed")
        fdm["propulsion/set-running"] = -1.0
        try:
            fdm.do_trim(0)
        except jsbsim.TrimFailureError as error:
            raise RuntimeError("JSBSim longitudinal teacher trim failed") from error
        self._target_pitch_rad = float(fdm["attitude/theta-rad"])
        self._teacher_aileron = float(fdm["fcs/aileron-cmd-norm"])
        self._teacher_rudder = float(fdm["fcs/rudder-cmd-norm"])
        self._teacher_throttle = float(fdm["fcs/throttle-cmd-norm"])
        pitch_error_deg = float(
            options.get("initial_pitch_error_deg", self.np_random.uniform(-12.0, 12.0))
        )
        fdm["ic/theta-deg"] = math.degrees(self._target_pitch_rad) + pitch_error_deg
        if not fdm.run_ic():
            raise RuntimeError("JSBSim perturbed run_ic() failed")
        self._steps = 0
        self._previous_action.fill(0.0)
        return self._observation(), self._info()

    def step(self, action: np.ndarray):
        if self._fdm is None:
            raise RuntimeError("reset() must be called before step()")
        action = np.asarray(action, dtype=np.float32)
        if action.shape != (1,) or not np.isfinite(action).all():
            raise ValueError("action must be a finite float array with shape (1,)")
        raw = float(np.clip(action[0], -1.0, 1.0))
        previous = float(self._previous_action[0])
        limited = previous + float(np.clip(raw - previous, -0.10, 0.10))
        applied = previous + 0.35 * (limited - previous)
        fdm = self._fdm
        fdm["fcs/aileron-cmd-norm"] = self._teacher_aileron
        fdm["fcs/elevator-cmd-norm"] = applied
        fdm["fcs/rudder-cmd-norm"] = self._teacher_rudder
        fdm["fcs/throttle-cmd-norm"] = self._teacher_throttle
        for _ in range(self.action_repeat):
            if not fdm.run():
                raise RuntimeError("JSBSim stopped before the episode ended")
        self._steps += 1
        pitch_error = math.atan2(
            math.sin(float(fdm["attitude/theta-rad"]) - self._target_pitch_rad),
            math.cos(float(fdm["attitude/theta-rad"]) - self._target_pitch_rad),
        )
        action_delta = abs(applied - previous)
        reward = -abs(pitch_error) - 0.002 * applied**2 - 0.02 * action_delta
        self._previous_action = np.asarray([applied], dtype=np.float32)
        observation = self._observation()
        finite = bool(np.isfinite(observation).all())
        terminated = not finite or float(fdm["position/h-agl-ft"]) <= 0.0
        truncated = self._steps >= round(self.episode_seconds * self.policy_hz)
        return observation, reward, terminated, truncated, self._info()

    def _observation(self) -> np.ndarray:
        assert self._fdm is not None
        fdm = self._fdm
        phi, theta, psi = (float(fdm[p]) for p in (
            "attitude/phi-rad", "attitude/theta-rad", "attitude/psi-rad"
        ))
        return np.asarray([
            math.sin(phi), math.cos(phi), math.sin(theta), math.cos(theta),
            math.sin(psi), math.cos(psi),
            fdm["velocities/p-rad_sec"], fdm["velocities/q-rad_sec"],
            fdm["velocities/r-rad_sec"], fdm["velocities/vc-kts"] / 500.0,
            fdm["position/h-sl-ft"] / 50_000.0, fdm["velocities/h-dot-fps"] / 1_000.0,
            math.sin(self._target_pitch_rad), math.cos(self._target_pitch_rad),
            self._previous_action[0], 1.0 / self.policy_hz,
        ], dtype=np.float32)

    def _info(self) -> dict[str, Any]:
        assert self._fdm is not None
        return {
            "model": "F-16-like JSBSim baseline (not Block 50 validated)",
            "sim_time_s": float(self._fdm.get_sim_time()),
            "lesson_id": "M01.2",
            "target_pitch_deg": math.degrees(self._target_pitch_rad),
        }

    def get_state_snapshot(self) -> dict[str, float | str]:
        assert self._fdm is not None
        return {
            "schema": "pilot-f16.replay-state.v1",
            "sim_time_s": float(self._fdm.get_sim_time()),
            "pitch_rad": float(self._fdm["attitude/theta-rad"]),
            "target_pitch_rad": self._target_pitch_rad,
            "pitch_rate_rad_s": float(self._fdm["velocities/q-rad_sec"]),
            "elevator_cmd_norm": float(self._previous_action[0]),
            "roll_rad": float(self._fdm["attitude/phi-rad"]),
            "altitude_ft": float(self._fdm["position/h-sl-ft"]),
            "airspeed_kts": float(self._fdm["velocities/vc-kts"]),
        }

    def close(self) -> None:
        self._fdm = None
