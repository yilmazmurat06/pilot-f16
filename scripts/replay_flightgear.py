from __future__ import annotations

import argparse
import json
import subprocess
import time
from pathlib import Path

import numpy as np

from pilot_f16 import F16BankEnv, F16BaselineEnv, F16PitchEnv


def main() -> None:
    parser = argparse.ArgumentParser(description="Replay an authoritative JSBSim episode in FlightGear")
    parser.add_argument(
        "--replay",
        type=Path,
        default=Path("artifacts/evaluation_m01_1/replay.json"),
    )
    parser.add_argument(
        "--fgfs",
        type=Path,
        default=Path(r"C:\Program Files\FlightGear 2024.1\bin\fgfs.exe"),
    )
    parser.add_argument("--aircraft-root", type=Path, default=Path("external/flightgear-aircraft"))
    parser.add_argument(
        "--fg-root",
        type=Path,
        default=Path("external/flightgear-data/fgdata_2024_1"),
    )
    parser.add_argument("--startup-seconds", type=float, default=35.0)
    parser.add_argument(
        "--auto-close",
        action="store_true",
        help="Close FlightGear automatically when the replay ends",
    )
    args = parser.parse_args()
    data = json.loads(args.replay.read_text(encoding="utf-8"))
    if data["schema"] != "pilot-f16.action-replay.v1":
        raise ValueError("Unsupported replay schema")
    version_file = args.fg_root / "version"
    if not version_file.is_file():
        raise FileNotFoundError(
            f"FlightGear data is missing at {args.fg_root}. "
            "Install the matching 2024.1.6 fgdata package first."
        )
    version = version_file.read_text(encoding="utf-8").strip()
    if version != "2024.1.6":
        raise RuntimeError(f"FlightGear data version mismatch: expected 2024.1.6, got {version}")
    command = [
        str(args.fgfs),
        f"--fg-root={args.fg_root.resolve()}",
        "--fdm=null",
        "--native-fdm=socket,in,60,,5600,udp",
        f"--fg-aircraft={args.aircraft_root.resolve()}",
        "--aircraft=f16-block-50",
        "--disable-terrasync",
        "--timeofday=noon",
        "--prop:/sim/current-view/view-number=1",
    ]
    print(f"FlightGear başlatılıyor; model yüklemesi için {args.startup_seconds:.0f} saniye beklenecek...")
    flightgear = subprocess.Popen(command)
    try:
        time.sleep(args.startup_seconds)
        if flightgear.poll() is not None:
            raise RuntimeError(f"FlightGear exited during startup with code {flightgear.returncode}")
        print("FlightGear hazır. JSBSim replay yayını başladı (yaklaşık 30 saniye).")
        env_types = {"M01.1": F16BaselineEnv, "M01.2": F16PitchEnv, "M01.3": F16BankEnv}
        env_type = env_types.get(data.get("lesson_id"), F16BaselineEnv)
        env = env_type(output_directive=Path("config/flightgear_output.xml"))
        env.reset(seed=int(data["seed"]), options=data.get("options"))
        wall_step = 1.0 / env.policy_hz
        for values in data["actions"]:
            started = time.perf_counter()
            _, _, terminated, truncated, _ = env.step(np.asarray(values, dtype=np.float32))
            time.sleep(max(0.0, wall_step - (time.perf_counter() - started)))
            if terminated or truncated:
                break
        env.close()
        time.sleep(2.0)
        print("Replay tamamlandı.")
        if not args.auto_close:
            input("Replay tamamlandı. FlightGear'ı kapatmak için Enter'a basın...")
    finally:
        flightgear.terminate()
        try:
            flightgear.wait(timeout=10)
        except subprocess.TimeoutExpired:
            flightgear.kill()


if __name__ == "__main__":
    main()
