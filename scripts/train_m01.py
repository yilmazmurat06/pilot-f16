from __future__ import annotations

import argparse
from pathlib import Path

from stable_baselines3 import PPO
from stable_baselines3.common.env_checker import check_env

from pilot_f16 import F16BankEnv, F16BaselineEnv, F16PitchEnv


def main() -> None:
    parser = argparse.ArgumentParser(description="Train the M01.1 baseline policy")
    parser.add_argument("--steps", type=int, default=100_000)
    parser.add_argument("--lesson", choices=("M01.1", "M01.2", "M01.3"), default="M01.1")
    parser.add_argument("--seed", type=int, default=20260818)
    parser.add_argument("--device", choices=("cpu", "cuda", "auto"), default="cpu")
    parser.add_argument("--output", type=Path, default=Path("artifacts/m01_1_ppo"))
    args = parser.parse_args()
    env_types = {"M01.1": F16BaselineEnv, "M01.2": F16PitchEnv, "M01.3": F16BankEnv}
    env = env_types[args.lesson]()
    check_env(env)
    model = PPO("MlpPolicy", env, seed=args.seed, verbose=1, device=args.device)
    model.learn(total_timesteps=args.steps, progress_bar=False)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    model.save(args.output)
    env.close()


if __name__ == "__main__":
    main()
