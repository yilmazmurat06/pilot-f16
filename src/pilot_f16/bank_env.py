"""M01.3 bank-angle tracking curriculum environment."""

from __future__ import annotations

from typing import Any

import numpy as np

from .env import F16BaselineEnv


class F16BankEnv(F16BaselineEnv):
    """Track non-zero bank targets while the teacher holds other axes."""

    def reset(self, *, seed: int | None = None, options: dict[str, Any] | None = None):
        options = dict(options or {})
        rng = np.random.default_rng(seed)
        target = float(options.get("target_roll_deg", rng.uniform(-45.0, 45.0)))
        error = float(options.get("initial_roll_error_deg", rng.uniform(-30.0, 30.0)))
        options["target_roll_deg"] = target
        options["initial_roll_deg"] = max(-70.0, min(70.0, target + error))
        observation, info = super().reset(seed=seed, options=options)
        info["lesson_id"] = "M01.3"
        info["target_roll_deg"] = target
        return observation, info

    def _info(self):
        info = super()._info()
        info["lesson_id"] = "M01.3"
        info["target_roll_deg"] = self._target_roll_rad * 180.0 / 3.141592653589793
        return info
