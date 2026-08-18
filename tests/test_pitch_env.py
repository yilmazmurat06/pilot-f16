import numpy as np

from pilot_f16 import F16PitchEnv


def test_pitch_reset_step_and_rate_limit() -> None:
    env = F16PitchEnv(episode_seconds=1.0)
    observation, info = env.reset(seed=11, options={"initial_pitch_error_deg": 10.0})
    assert observation.shape == (16,)
    assert info["lesson_id"] == "M01.2"
    observation, reward, terminated, truncated, _ = env.step(np.ones(1, dtype=np.float32))
    state = env.get_state_snapshot()
    assert np.isfinite(observation).all() and np.isfinite(reward)
    assert abs(float(state["elevator_cmd_norm"])) <= 0.0351
    assert not (terminated and truncated)
