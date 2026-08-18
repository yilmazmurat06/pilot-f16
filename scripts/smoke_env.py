from __future__ import annotations

import hashlib
import json

import numpy as np

from pilot_f16 import F16BaselineEnv


def rollout(seed: int) -> str:
    env = F16BaselineEnv(episode_seconds=2.0)
    observation, info = env.reset(seed=seed)
    states = [observation.tolist()]
    action = np.asarray([0.05], dtype=np.float32)
    for _ in range(20):
        observation, _, terminated, truncated, _ = env.step(action)
        states.append(observation.tolist())
        if terminated or truncated:
            break
    env.close()
    payload = json.dumps(states, separators=(",", ":"), allow_nan=False).encode()
    digest = hashlib.sha256(payload).hexdigest()
    print(f"{info['model']} | state_sha256={digest}")
    return digest


if __name__ == "__main__":
    first = rollout(20260818)
    second = rollout(20260818)
    if first != second:
        raise SystemExit("determinism smoke test FAILED")
    print("determinism smoke test PASSED")
