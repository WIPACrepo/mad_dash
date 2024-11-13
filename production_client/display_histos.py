"""Display the histograms in a file."""

import argparse
import json
import pickle
from pathlib import Path

import h5py
import matplotlib.pyplot as plt
import numpy as np


def from_hdf5(fpath: Path):
    """Load a non-nested dictionary from an HDF5 file."""
    data_dict = {}

    with h5py.File(fpath) as f:
        for key in f.keys():
            sub_dict = {}

            # Read each dataset within the group
            for sub_key, item in f[key].items():
                if isinstance(item, h5py.Dataset):
                    data = item[()]
                    if isinstance(data, np.ndarray):
                        sub_dict[sub_key] = data.tolist()
                    else:
                        sub_dict[sub_key] = data

            # Read each attribute within the group
            for attr_key, attr_value in f[key].attrs.items():
                # Check if the attribute is NaN, and convert it back to None
                if isinstance(attr_value, float) and np.isnan(attr_value):
                    sub_dict[attr_key] = None
                else:
                    sub_dict[attr_key] = attr_value

            data_dict[key] = sub_dict

    return data_dict


def main():
    """Display them."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "path",
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
    elif args.path.suffix in [".hdf5"]:
        histograms = from_hdf5(args.path)
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


if __name__ == "__main__":
    main()
