import math

import numpy as np

from pilot_f16 import F16BankEnv


def test_bank_target_is_exposed_and_deterministic() -> None:
    env = F16BankEnv(episode_seconds=1.0)
    observation, info = env.reset(
        seed=12, options={"target_roll_deg": 30.0, "initial_roll_error_deg": -15.0}
    )
    state = env.get_state_snapshot()
    assert observation.shape == (16,)
    assert info["lesson_id"] == "M01.3"
    assert math.isclose(math.degrees(float(state["target_roll_rad"])), 30.0, abs_tol=1e-6)
    observation, reward, _, _, _ = env.step(np.zeros(1, dtype=np.float32))
    assert np.isfinite(observation).all() and np.isfinite(reward)
