#!/usr/bin/env python3
"""Compare every red agent against every blue agent across the MATRIX variants.

For each variant (availability, confidentiality, integrity), each of its five
fixed scenarios (Scenario2_SIS_1..5), each red/blue pairing and each seed, this
plays one game and records how it went. Results are averaged per pairing.

All three variants install under the same package name ("CybORG"), so each
variant runs in its own subprocess with that variant first on PYTHONPATH.

Usage (from the repo root, venv active or not):
    python compare_agents.py                      # all variants, 20 seeds
    python compare_agents.py --seeds 50 --steps 30
    python compare_agents.py --variants integrity --scenarios 1 4

Outputs (in --out, default results/):
    games_<variant>.csv   one row per game
    summary.csv           mean/std per variant x red x blue (over scenarios+seeds)
    summary_by_scenario.csv
    summary.md            readable tables
"""
import argparse
import os
import subprocess
import sys
import time

REPO = os.path.dirname(os.path.abspath(__file__))
VARIANTS = ["availability", "confidentiality", "integrity"]
SCENARIO_DIR = {
    "availability": "SIS_Availability_Scenarios",
    "confidentiality": "SIS_Confidentiality_Scenarios",
    "integrity": "SIS_Integrity_Scenarios",
}
# Agent class names per variant (each variant ships a slightly different set).
RED_AGENTS = {
    "B_line": "B_lineAgent_SIS_random",
    "Meander": "RedMeanderAgent_SIS_random",
}
BLUE_AGENTS = {
    "availability": {
        "Monitor": "BlueMonitorAgent",
        "ReactRemove": "BlueReactRemoveAgent",
        "ReactRestore": "BlueReactRestoreAgent",
    },
    "confidentiality": {
        "Monitor": "BlueMonitorAgent",
        "ReactRemove": "BlueReactRemoveAgent",
        "ReactRestore": "BlueReactRestoreAgent",
        "ReactBlock": "BlueReactBlockAgent",
    },
    "integrity": {
        "Monitor": "BlueMonitorAgent",
        "ReactRemove": "BlueReactRemoveAgent",
        "ReactRestore": "BlueReactRestoreAgent",
        "ReactRemoveRestoreContent": "BlueReactRemoveRestoreContentAgent",
    },
}
GAME_FIELDS = [
    "variant", "scenario", "red", "blue", "seed", "steps_played", "error",
    "blue_total", "blue_final_step", "first_loss_step",
    "red_impacts", "first_impact_step", "blue_actions",
]


# --------------------------------------------------------------------------
# Worker: runs inside one variant's subprocess
# --------------------------------------------------------------------------
def run_worker(args):
    import csv
    import inspect
    import random
    import warnings
    from multiprocessing import Pool

    import numpy as np  # noqa: F401  (seeded below)

    warnings.filterwarnings("ignore")
    import CybORG as cyborg_pkg
    expected = os.path.join(REPO, f"cc5_sis_{args.variant}")
    if not os.path.abspath(cyborg_pkg.__file__).startswith(expected):
        sys.exit(f"[{args.variant}] imported the wrong CybORG: {cyborg_pkg.__file__}")

    jobs = []
    for scen in args.scenarios:
        for red in RED_AGENTS:
            for blue in BLUE_AGENTS[args.variant]:
                for seed in range(args.seeds):
                    jobs.append((args.variant, scen, red, blue, seed, args.steps))

    out_path = os.path.join(args.out, f"games_{args.variant}.csv")
    t0 = time.time()
    with Pool(args.jobs) as pool, open(out_path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=GAME_FIELDS)
        writer.writeheader()
        for i, row in enumerate(pool.imap_unordered(play_game, jobs, chunksize=4), 1):
            writer.writerow(row)
            if i % 50 == 0 or i == len(jobs):
                print(f"[{args.variant}] {i}/{len(jobs)} games ({time.time() - t0:.0f}s)", flush=True)


def play_game(job):
    import inspect
    import random
    import sys
    import warnings
    from collections import Counter

    import gymnasium as gym
    import numpy as np

    sys.modules["gym"] = gym
    warnings.filterwarnings("ignore")
    from CybORG import CybORG
    import CybORG.Agents as agents
    from CybORG.Shared.Actions import Impact
    from CybORG.Shared.Enums import TrinaryEnum

    variant, scen, red, blue, seed, steps = job
    row = dict(variant=variant, scenario=scen, red=red, blue=blue, seed=seed,
               steps_played=0, error="", blue_total=0.0, blue_final_step=0.0,
               first_loss_step="", red_impacts=0, first_impact_step="", blue_actions="")

    random.seed(seed)
    np.random.seed(seed)
    scenario_file = (str(inspect.getfile(CybORG))[:-10]
                     + f"/Shared/Scenarios/{SCENARIO_DIR[variant]}/Scenario2_SIS_{scen}.yaml")
    game_agents = {
        "Red": getattr(agents, RED_AGENTS[red]),
        "Blue": getattr(agents, BLUE_AGENTS[variant][blue]),
    }
    # Confidentiality ships no GreenConsumeAgent; the others use it as normal users.
    if hasattr(agents, "GreenConsumeAgent"):
        game_agents["Green"] = agents.GreenConsumeAgent

    blue_acts = Counter()
    try:
        env = CybORG(scenario_file, "sim", agents=game_agents,
                     random_red_init=False, random_topologies=False)
        env.set_seed(seed)
        env.reset()
        for step in range(steps):
            env.step()
            r = env.get_rewards()["Blue"]
            row["blue_total"] += r
            row["blue_final_step"] = r
            row["steps_played"] = step + 1
            if r < 0 and row["first_loss_step"] == "":
                row["first_loss_step"] = step
            red_action = env.get_last_action("Red")
            if (isinstance(red_action, Impact)
                    and env.get_observation("Red").get("success") == TrinaryEnum.TRUE):
                row["red_impacts"] += 1
                if row["first_impact_step"] == "":
                    row["first_impact_step"] = step
            blue_acts[type(env.get_last_action("Blue")).__name__] += 1
    except Exception as exc:  # record and keep going; one bad game shouldn't stop the sweep
        row["error"] = f"{type(exc).__name__}: {exc}"[:200]

    row["blue_total"] = round(row["blue_total"], 2)
    row["blue_actions"] = ";".join(f"{k}={v}" for k, v in sorted(blue_acts.items()))
    return row


# --------------------------------------------------------------------------
# Driver: launches one subprocess per variant, then summarises
# --------------------------------------------------------------------------
def run_driver(args):
    os.makedirs(args.out, exist_ok=True)
    python = os.path.join(REPO, "venv", "bin", "python")
    if not os.path.exists(python):
        python = sys.executable

    procs = []
    for v in args.variants:
        env = dict(os.environ)
        env["PYTHONPATH"] = os.path.join(REPO, f"cc5_sis_{v}", "CybORG")
        cmd = [python, "-W", "ignore", __file__, "--worker", "--variant", v,
               "--seeds", str(args.seeds), "--steps", str(args.steps),
               "--jobs", str(args.jobs), "--out", args.out,
               "--scenarios", *map(str, args.scenarios)]
        procs.append((v, subprocess.Popen(cmd, env=env)))
    failed = [v for v, p in procs if p.wait() != 0]
    if failed:
        sys.exit(f"Variant run(s) failed: {', '.join(failed)}")
    summarise(args)


def summarise(args):
    import pandas as pd

    games = pd.concat(
        [pd.read_csv(os.path.join(args.out, f"games_{v}.csv")) for v in args.variants],
        ignore_index=True,
    )
    errors = games[games["error"].notna()]
    ok = games[games["error"].isna()].copy()
    ok["impacted"] = ok["red_impacts"] > 0

    def agg(df, keys):
        g = df.groupby(keys)
        out = g.agg(
            games=("blue_total", "size"),
            blue_mean=("blue_total", "mean"),
            blue_std=("blue_total", "std"),
            blue_median=("blue_total", "median"),
            final_step_mean=("blue_final_step", "mean"),
            impact_rate=("impacted", "mean"),
            impacts_mean=("red_impacts", "mean"),
            first_loss_mean=("first_loss_step", "mean"),
        ).reset_index()
        return out.round(2)

    overall = agg(ok, ["variant", "red", "blue"])
    by_scen = agg(ok, ["variant", "scenario", "red", "blue"])
    overall.to_csv(os.path.join(args.out, "summary.csv"), index=False)
    by_scen.to_csv(os.path.join(args.out, "summary_by_scenario.csv"), index=False)

    lines = [
        "# Red vs. blue agent comparison",
        "",
        f"- Variants: {', '.join(args.variants)}; scenarios {args.scenarios}; "
        f"{args.seeds} seeds each; {args.steps} steps per game",
        f"- Games played: {len(games)} ({len(errors)} errored)",
        "- `blue_mean` = average total blue reward per game (closer to 0 is better for blue)",
        "- `impact_rate` = share of games where red landed at least one successful Impact",
        "- `final_step_mean` = blue reward on the last step (how bad things are when the game ends)",
        "",
    ]
    for v in args.variants:
        lines.append(f"## {v}")
        lines.append("")
        for red in RED_AGENTS:
            sub = overall[(overall.variant == v) & (overall.red == red)].sort_values(
                "blue_mean", ascending=False)
            if sub.empty:
                continue
            best = sub.iloc[0]["blue"]
            lines.append(f"### vs. {red} (best defender: **{best}**)")
            lines.append("")
            lines.append(sub.drop(columns=["variant", "red"]).to_markdown(index=False))
            lines.append("")
        pivot = by_scen[by_scen.variant == v].pivot_table(
            index=["red", "blue"], columns="scenario", values="blue_mean")
        lines.append("Mean blue total by scenario:")
        lines.append("")
        lines.append(pivot.round(1).to_markdown())
        lines.append("")
    if len(errors):
        lines.append("## Errors")
        lines.append("")
        lines.append(errors.groupby(["variant", "red", "blue", "error"]).size()
                     .rename("games").reset_index().to_markdown(index=False))
        lines.append("")
    with open(os.path.join(args.out, "summary.md"), "w") as fh:
        fh.write("\n".join(lines))
    print("\n".join(lines))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--variants", nargs="+", default=VARIANTS, choices=VARIANTS)
    p.add_argument("--scenarios", nargs="+", type=int, default=[1, 2, 3, 4, 5])
    p.add_argument("--seeds", type=int, default=20, help="games per pairing per scenario")
    p.add_argument("--steps", type=int, default=30, help="steps per game")
    p.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 3) // 3),
                   help="parallel games per variant")
    p.add_argument("--out", default=os.path.join(REPO, "results"))
    p.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    p.add_argument("--variant", help=argparse.SUPPRESS)
    p.add_argument("--summarise-only", action="store_true",
                   help="rebuild the summary from existing games_*.csv files")
    args = p.parse_args()
    args.out = os.path.abspath(args.out)
    if args.worker:
        run_worker(args)
    elif args.summarise_only:
        summarise(args)
    else:
        run_driver(args)


if __name__ == "__main__":
    main()
