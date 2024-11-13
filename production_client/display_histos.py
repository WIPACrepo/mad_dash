"""Display the histograms in a file."""

import argparse
import json
import pickle
from pathlib import Path

import matplotlib.pyplot as plt


def main():
    """Display them."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "path",
        nargs="1",
        type=Path,
        help="the dataset directory to grab pickled histograms",
    )
    args = parser.parse_args()
    args.path: Path  # typehint to aid IDE

    # get histograms
    if args.path.suffix in [".pickle", ".pkl"]:
        with open(args.path, "rb") as f:
            histograms = pickle.load(f)
    elif args.path.suffix in [".json"]:
        with open(args.path) as f:
            histograms = json.load(f)
    else:
        raise RuntimeError(f"Unrecognized file type: {args.path}")

    # display with matplotlib
    for histo in histograms.values():
        num_bins = len(histo["bin_values"])
        x_values = [
            histo["xmin"] + (histo["xmax"] - histo["xmin"]) * i / (num_bins - 1)
            for i in range(num_bins)
        ]

        # Plotting the bin values
        plt.figure(figsize=(8, 6))
        plt.bar(
            x_values,
            histo["bin_values"],
            width=(histo["xmax"] - histo["xmin"]) / num_bins,
            align="center",
        )
        plt.xlabel("Bins")
        plt.ylabel("Values")
        plt.title(histo["name"])
        if sub := histo.get("_dataset_path"):
            plt.suptitle(sub, fontsize=10, y=0.95)
        plt.show()
