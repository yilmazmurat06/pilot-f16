from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Callable

import matplotlib.pyplot as plt
import numpy as np
from stable_baselines3 import PPO

from pilot_f16 import F16BaselineEnv

Policy = Callable[[np.ndarray], np.ndarray]


def run_episode(policy: Policy, seed: int, initial_roll_deg: float, capture: bool = False):
    env = F16BaselineEnv()
    observation, _ = env.reset(seed=seed, options={"initial_roll_deg": initial_roll_deg})
    rewards: list[float] = []
    errors: list[float] = []
    actions: list[float] = []
    applied_actions: list[float] = []
    telemetry: list[dict[str, float]] = []
    initial_altitude = float(env.get_state_snapshot()["altitude_ft"])
    terminated = truncated = False
    while not (terminated or truncated):
        action = np.asarray(policy(observation), dtype=np.float32).reshape(1)
        observation, reward, terminated, truncated, _ = env.step(action)
        state = env.get_state_snapshot()
        roll_deg = math.degrees(float(state["roll_rad"]))
        error = abs(roll_deg)
        rewards.append(float(reward))
        errors.append(error)
        actions.append(float(action[0]))
        applied_actions.append(float(state["aileron_cmd_norm"]))
        if capture:
            telemetry.append(
                {
                    "time_s": float(state["sim_time_s"]),
                    "roll_deg": roll_deg,
                    "target_roll_deg": 0.0,
                    "roll_error_deg": error,
                    "roll_rate_deg_s": math.degrees(float(state["roll_rate_rad_s"])),
                    "aileron_cmd_norm": float(state["aileron_cmd_norm"]),
                    "policy_action_norm": float(action[0]),
                    "altitude_ft": float(state["altitude_ft"]),
                    "airspeed_kts": float(state["airspeed_kts"]),
                }
            )
    final_samples = errors[-10 * env.policy_hz :]
    result = {
        "seed": seed,
        "initial_roll_deg": initial_roll_deg,
        "return": float(sum(rewards)),
        "roll_mae_deg": float(np.mean(errors)),
        "final_10s_roll_mae_deg": float(np.mean(final_samples)),
        "max_roll_error_deg": float(np.max(errors)),
        "final_roll_error_deg": float(errors[-1]),
        "control_total_variation": float(np.abs(np.diff(applied_actions)).sum()),
        "max_abs_aileron": float(np.max(np.abs(applied_actions))),
        "altitude_deviation_ft": float(abs(float(state["altitude_ft"]) - initial_altitude)),
        "terminated": bool(terminated),
        "success": bool(np.mean(final_samples) <= 2.0 and not terminated),
        "steps": len(rewards),
    }
    env.close()
    return result, telemetry, actions


def aggregate(results: list[dict]) -> dict[str, float | int]:
    return {
        "episodes": len(results),
        "success_rate": float(np.mean([r["success"] for r in results])),
        "mean_return": float(np.mean([r["return"] for r in results])),
        "mean_roll_mae_deg": float(np.mean([r["roll_mae_deg"] for r in results])),
        "mean_final_10s_roll_mae_deg": float(
            np.mean([r["final_10s_roll_mae_deg"] for r in results])
        ),
        "mean_control_total_variation": float(
            np.mean([r["control_total_variation"] for r in results])
        ),
        "mean_altitude_deviation_ft": float(
            np.mean([r["altitude_deviation_ft"] for r in results])
        ),
        "terminations": int(sum(r["terminated"] for r in results)),
    }


def write_telemetry(path: Path, rows: list[dict[str, float | str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def plot_telemetry(path: Path, rows_by_policy: dict[str, list[dict[str, float]]]) -> None:
    fig, axes = plt.subplots(3, 1, figsize=(11, 9), sharex=True)
    for name, rows in rows_by_policy.items():
        t = [r["time_s"] for r in rows]
        axes[0].plot(t, [r["roll_deg"] for r in rows], label=name)
        axes[1].plot(t, [r["aileron_cmd_norm"] for r in rows], label=name)
        axes[2].plot(t, [r["altitude_ft"] for r in rows], label=name)
    axes[0].axhline(0.0, color="black", linestyle="--", linewidth=1, label="target")
    axes[0].set_ylabel("Roll (deg)")
    axes[1].set_ylabel("Aileron command")
    axes[2].set_ylabel("Altitude (ft)")
    axes[2].set_xlabel("JSBSim time (s)")
    for axis in axes:
        axis.grid(True, alpha=0.3)
        axis.legend()
    fig.suptitle("M01.1 trained policy vs baselines (+30 deg initial roll)")
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=160)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description="Strict M01.1 evaluation with baselines")
    parser.add_argument("--model", type=Path, default=Path("artifacts/m01_1_ppo_v3.zip"))
    parser.add_argument("--episodes", type=int, default=200)
    parser.add_argument("--seed", type=int, default=20260818)
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/evaluation_m01_1"))
    args = parser.parse_args()
    model = PPO.load(args.model, device="cpu")
    random_rng = np.random.default_rng(args.seed + 999_999)
    policies: dict[str, Policy] = {
        "trained": lambda obs: model.predict(obs, deterministic=True)[0],
        "zero": lambda obs: np.zeros(1, dtype=np.float32),
        "random": lambda obs: random_rng.uniform(-1.0, 1.0, 1).astype(np.float32),
    }
    initial_rolls = np.linspace(-30.0, 30.0, args.episodes, dtype=float)
    all_results: dict[str, list[dict]] = {name: [] for name in policies}
    captured: dict[str, list[dict[str, float]]] = {}
    replay_actions: list[float] = []
    capture_seed = args.seed + args.episodes
    for name, policy in policies.items():
        for episode, initial_roll in enumerate(initial_rolls):
            result, _, _ = run_episode(policy, args.seed + episode, float(initial_roll))
            result["episode"] = episode
            all_results[name].append(result)
        _, telemetry, actions = run_episode(policy, capture_seed, 30.0, capture=True)
        captured[name] = telemetry
        if name == "trained":
            replay_actions = actions

    summaries = {name: aggregate(results) for name, results in all_results.items()}
    trained = summaries["trained"]
    zero = summaries["zero"]
    improvement_ratio = float(
        trained["mean_final_10s_roll_mae_deg"] / zero["mean_final_10s_roll_mae_deg"]
    )
    acceptance = {
        "minimum_episodes": 200,
        "required_success_rate": 0.95,
        "required_final_10s_mae_deg": 2.0,
        "required_vs_zero_ratio": 0.5,
        "maximum_control_total_variation": 30.0,
        "maximum_mean_altitude_deviation_ft": 1500.0,
        "actual_vs_zero_ratio": improvement_ratio,
        "pass": bool(
            args.episodes >= 200
            and trained["success_rate"] >= 0.95
            and trained["mean_final_10s_roll_mae_deg"] <= 2.0
            and improvement_ratio <= 0.5
            and trained["mean_control_total_variation"] <= 30.0
            and trained["mean_altitude_deviation_ft"] <= 1500.0
            and trained["terminations"] == 0
        ),
    }
    report = {
        "schema": "pilot-f16.m01-strict-evaluation.v2",
        "model": str(args.model),
        "scenario": "initial roll evenly spans -30..+30 deg; target roll 0 deg",
        "summaries": summaries,
        "acceptance": acceptance,
        "episode_results": all_results,
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    report_path = args.output_dir / "report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    flat_rows = [dict(policy=name, **row) for name, rows in captured.items() for row in rows]
    write_telemetry(args.output_dir / "telemetry.csv", flat_rows)
    plot_telemetry(args.output_dir / "telemetry.png", captured)
    replay = {
        "schema": "pilot-f16.action-replay.v1",
        "model": str(args.model),
        "seed": capture_seed,
        "lesson_id": "M01.1",
        "options": {"initial_roll_deg": 30.0},
        "physics_hz": F16BaselineEnv.physics_hz,
        "policy_hz": F16BaselineEnv.policy_hz,
        "actions": [[value] for value in replay_actions],
    }
    (args.output_dir / "replay.json").write_text(
        json.dumps(replay, separators=(",", ":")), encoding="utf-8"
    )
    print(json.dumps({"summaries": summaries, "acceptance": acceptance}, indent=2))
    print(f"report={report_path}")
    print(f"telemetry={args.output_dir / 'telemetry.csv'}")
    print(f"plot={args.output_dir / 'telemetry.png'}")


if __name__ == "__main__":
    main()
