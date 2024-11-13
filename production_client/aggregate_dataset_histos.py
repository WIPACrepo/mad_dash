"""Aggregate the dataset's job's histograms, by sampling."""

import argparse
import asyncio
import json
import logging
import pickle
import random
from pathlib import Path
from typing import Iterator

SKIP_KEYS = ["filelist"]
HISTO_TYPES = [
    "PrimaryZenith",
    "PrimaryCosZenith",
    "PrimaryEnergy",
    "PrimaryType",
    "PrimaryMultiplicity",
    "NMu",
    "SecondaryZenith",
    "SecondaryCosZenith",
    "SecondaryEnergy",
    "SecondaryType",
    "CascadeEnergy",
    "MuonLength",
    "TauLength",
    "LogMostEnergeticMuon",
]


def get_job_histo_files(dataset_dir: Path, sample_percentage: float) -> Iterator[Path]:
    """Yield a sample of histogram files, each originating from a job."""
    sample_percentage = max(0.0, min(sample_percentage, 1.0))

    all_histos = list((dataset_dir / "*/histos/*.pkl").glob("*"))
    random.shuffle(all_histos)
    sampled_histos = all_histos[: int(len(all_histos) * sample_percentage)]

    logging.info(
        f"sampling {sample_percentage * 100:.1f}% of histograms "
        f"({len(sampled_histos)}/{len(all_histos)} total)"
    )

    yield from sampled_histos


def update_aggregation(existing: dict, new: dict) -> dict:
    """Incorporate the 'new' histogram with the existing aggregated histogram.

    Note: Does not normalize data
    """
    if new["name"] != existing["name"]:
        logging.warning(
            f"new histogram '{new["name"]}' does not match existing histogram '{existing['name']}'"
        )

    existing.update(
        {
            "xmin": min(existing["xmin"], new["xmin"]),
            "xmax": max(existing["xmax"], new["xmax"]),
            "overflow": None,  # TOD0
            "underflow": None,  # TOD0
            "nan_count": existing["nan_count"] + new["nan_count"],
            "bin_values": [
                a + b for a, b in zip(existing["bin_values"], new["bin_values"])
            ],
            "_sample_count": existing["_sample_count"] + 1,
        }
    )

    return existing


async def main() -> None:
    """Do main."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "path",
        nargs="1",
        type=Path,
        help="the dataset directory to grab pickled histograms",
    )
    parser.add_argument(
        "--sample-percentage",
        type=float,
        required=True,
        help="the percentage of a dataset's histogram to be sampled (for each type)",
    )
    parser.add_argument(
        "--dest-dir",
        type=Path,
        required=True,
        help="the destination directory to write a json file containing aggregated histograms",
    )
    args = parser.parse_args()
    args.path: Path  # typehint to aid IDE
    args.dest_dir: Path  # ^^^

    agg_histograms = {
        t: {
            "name": t,
            "xmin": None,
            "xmax": None,
            "overflow": None,
            "underflow": None,
            "nan_count": None,
            "bin_values": [],
            "_sample_count": 0,
        }
        for t in HISTO_TYPES
    }

    # build aggregated histograms
    for job_file in get_job_histo_files(args.path, args.sample_percentage):
        with open(job_file, "rb") as f:
            contents = pickle.load(f)
            for histo_type in contents.keys():
                if histo_type in SKIP_KEYS:
                    continue
                elif histo_type not in HISTO_TYPES:
                    logging.warning(f"unknown histogram type: {histo_type}")
                    continue
                # grab data
                agg_histograms[histo_type] = update_aggregation(
                    agg_histograms[histo_type], contents[histo_type]
                )

    # average data
    for histo in agg_histograms.values():
        histo.update(
            {
                "bin_values": [x / histo["_sample_count"] for x in histo["bin_values"]],
            }
        )

    # write out aggregated-averaged histos
    with open(args.dest / f"{args.path.name}.json", "w") as f:
        json.dump(agg_histograms, f)  # don't indent


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
