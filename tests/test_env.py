import numpy as np

from pilot_f16 import F16BaselineEnv


def test_reset_and_step_are_finite() -> None:
    env = F16BaselineEnv(episode_seconds=1.0)
    observation, info = env.reset(seed=7)
    assert observation.shape == env.observation_space.shape
    assert np.isfinite(observation).all()
    observation, reward, terminated, truncated, _ = env.step(np.zeros(1, dtype=np.float32))
    assert np.isfinite(observation).all()
    assert np.isfinite(reward)
    assert not (terminated and truncated)
    assert info["lesson_id"] == "M01.1"


def test_same_seed_and_actions_are_deterministic() -> None:
    action = np.asarray([0.1], dtype=np.float32)
    trajectories = []
    for _ in range(2):
        env = F16BaselineEnv()
        states = [env.reset(seed=42)[0]]
        states.extend(env.step(action)[0] for _ in range(10))
        trajectories.append(np.stack(states))
    np.testing.assert_array_equal(*trajectories)


def test_roll_action_is_rate_limited() -> None:
    env = F16BaselineEnv()
    env.reset(seed=9, options={"initial_roll_deg": 20.0})
    env.step(np.ones(1, dtype=np.float32))
    first = float(env.get_state_snapshot()["aileron_cmd_norm"])
    env.step(-np.ones(1, dtype=np.float32))
    second = float(env.get_state_snapshot()["aileron_cmd_norm"])
    assert abs(first) <= 0.0351
    assert abs(second - first) <= 0.0351
