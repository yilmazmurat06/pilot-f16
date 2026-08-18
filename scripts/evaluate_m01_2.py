from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from stable_baselines3 import PPO

from pilot_f16 import F16PitchEnv


def episode(policy, seed: int, initial_error: float, capture: bool = False):
    env = F16PitchEnv()
    obs, _ = env.reset(seed=seed, options={"initial_pitch_error_deg": initial_error})
    errors, rewards, commands, rows = [], [], [], []
    initial_altitude = float(env.get_state_snapshot()["altitude_ft"])
    terminated = truncated = False
    raw_actions = []
    while not (terminated or truncated):
        action = np.asarray(policy(obs), dtype=np.float32).reshape(1)
        obs, reward, terminated, truncated, _ = env.step(action)
        state = env.get_state_snapshot()
        pitch = math.degrees(float(state["pitch_rad"]))
        target = math.degrees(float(state["target_pitch_rad"]))
        error = abs(pitch - target)
        errors.append(error)
        rewards.append(float(reward))
        commands.append(float(state["elevator_cmd_norm"]))
        raw_actions.append(float(action[0]))
        if capture:
            rows.append({
                "time_s": float(state["sim_time_s"]), "pitch_deg": pitch,
                "target_pitch_deg": target, "pitch_error_deg": error,
                "pitch_rate_deg_s": math.degrees(float(state["pitch_rate_rad_s"])),
                "elevator_cmd_norm": float(state["elevator_cmd_norm"]),
                "policy_action_norm": float(action[0]),
                "roll_deg": math.degrees(float(state["roll_rad"])),
                "altitude_ft": float(state["altitude_ft"]),
                "airspeed_kts": float(state["airspeed_kts"]),
            })
    final = errors[-10 * env.policy_hz:]
    result = {
        "seed": seed, "initial_pitch_error_deg": initial_error,
        "return": float(sum(rewards)), "pitch_mae_deg": float(np.mean(errors)),
        "final_10s_pitch_mae_deg": float(np.mean(final)),
        "final_pitch_error_deg": float(errors[-1]),
        "control_total_variation": float(np.abs(np.diff(commands)).sum()),
        "altitude_deviation_ft": abs(float(state["altitude_ft"]) - initial_altitude),
        "max_abs_roll_deg": float(max(abs(float(r["roll_deg"])) for r in rows)) if rows else 0.0,
        "terminated": bool(terminated),
        "success": bool(np.mean(final) <= 2.0 and not terminated),
    }
    env.close()
    return result, rows, raw_actions


def summary(results):
    return {
        "episodes": len(results),
        "success_rate": float(np.mean([r["success"] for r in results])),
        "mean_return": float(np.mean([r["return"] for r in results])),
        "mean_pitch_mae_deg": float(np.mean([r["pitch_mae_deg"] for r in results])),
        "mean_final_10s_pitch_mae_deg": float(np.mean([r["final_10s_pitch_mae_deg"] for r in results])),
        "mean_control_total_variation": float(np.mean([r["control_total_variation"] for r in results])),
        "mean_altitude_deviation_ft": float(np.mean([r["altitude_deviation_ft"] for r in results])),
        "terminations": int(sum(r["terminated"] for r in results)),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Strict M01.2 pitch evaluation")
    parser.add_argument("--model", type=Path, default=Path("artifacts/m01_2_ppo.zip"))
    parser.add_argument("--episodes", type=int, default=200)
    parser.add_argument("--seed", type=int, default=20260818)
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/evaluation_m01_2"))
    args = parser.parse_args()
    model = PPO.load(args.model, device="cpu")
    rng = np.random.default_rng(args.seed + 888_888)
    policies = {
        "trained": lambda obs: model.predict(obs, deterministic=True)[0],
        "zero": lambda obs: np.zeros(1, dtype=np.float32),
        "random": lambda obs: rng.uniform(-1, 1, 1).astype(np.float32),
    }
    results, captured, replay_actions = {}, {}, []
    for name, policy in policies.items():
        results[name] = [episode(policy, args.seed + i, float(v))[0]
                         for i, v in enumerate(np.linspace(-12, 12, args.episodes))]
        _, captured[name], actions = episode(policy, args.seed + args.episodes, 12.0, True)
        if name == "trained": replay_actions = actions
    summaries = {name: summary(value) for name, value in results.items()}
    trained, zero = summaries["trained"], summaries["zero"]
    ratio = trained["mean_final_10s_pitch_mae_deg"] / zero["mean_final_10s_pitch_mae_deg"]
    acceptance = {
        "minimum_episodes": 200, "required_success_rate": 0.95,
        "required_final_10s_mae_deg": 2.0, "required_vs_zero_ratio": 0.5,
        "maximum_control_total_variation": 30.0,
        "maximum_mean_altitude_deviation_ft": 2000.0,
        "actual_vs_zero_ratio": ratio,
        "pass": bool(args.episodes >= 200 and trained["success_rate"] >= .95
                     and trained["mean_final_10s_pitch_mae_deg"] <= 2
                     and ratio <= .5 and trained["mean_control_total_variation"] <= 30
                     and trained["mean_altitude_deviation_ft"] <= 2000
                     and trained["terminations"] == 0),
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    report = {"schema": "pilot-f16.m01-2-strict-evaluation.v1", "summaries": summaries,
              "acceptance": acceptance, "episode_results": results}
    (args.output_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    flat = [dict(policy=n, **r) for n, rows in captured.items() for r in rows]
    with (args.output_dir / "telemetry.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(flat[0])); writer.writeheader(); writer.writerows(flat)
    fig, axes = plt.subplots(3, 1, figsize=(11, 9), sharex=True)
    for name, rows in captured.items():
        t = [r["time_s"] for r in rows]
        axes[0].plot(t, [r["pitch_deg"] for r in rows], label=name)
        axes[1].plot(t, [r["elevator_cmd_norm"] for r in rows], label=name)
        axes[2].plot(t, [r["altitude_ft"] for r in rows], label=name)
    axes[0].axhline(captured["trained"][0]["target_pitch_deg"], color="black", ls="--", label="target")
    for ax, label in zip(axes, ("Pitch (deg)", "Elevator command", "Altitude (ft)")):
        ax.set_ylabel(label); ax.grid(alpha=.3); ax.legend()
    axes[2].set_xlabel("JSBSim time (s)"); fig.tight_layout()
    fig.savefig(args.output_dir / "telemetry.png", dpi=160); plt.close(fig)
    replay = {"schema": "pilot-f16.action-replay.v1", "model": str(args.model),
              "seed": args.seed + args.episodes, "lesson_id": "M01.2",
              "options": {"initial_pitch_error_deg": 12.0},
              "physics_hz": 120, "policy_hz": 20,
              "actions": [[v] for v in replay_actions]}
    (args.output_dir / "replay.json").write_text(json.dumps(replay, separators=(",", ":")), encoding="utf-8")
    print(json.dumps({"summaries": summaries, "acceptance": acceptance}, indent=2))


if __name__ == "__main__": main()
