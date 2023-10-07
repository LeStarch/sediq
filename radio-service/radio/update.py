import argparse
import sys

from pathlib import Path

def parse_arguments():
    """ Parse the command line arguments """
    parser = argparse.ArgumentParser(description="Write FM audio sample pairs to the given output file-path")
    parser.add_argument("--update-file", type=Path, help="Path to be checked for a file containing updates",
                        default=Path("/tmp/radio-update"))
    parser.add_argument("frequency", type=float, help="Initial frequency", default=89.3)
    return parser.parse_args()


def main():
    """ Main function, Hi Lewis!! """
    try:
        args = parse_arguments()
        frequency = args.frequency
        if frequency <= 108.0 and frequency >= 88.0:
            frequency = int(frequency * 1e6)
            with open(args.update_file, "w") as file_handle:
                print(f"Setting to: {frequency}")
                print(f"{frequency}", file=file_handle)
                sys.exit(0)
        else:
            print(f"[ERROR] Frequency out of range [88 MHz-108 MHz]: {frequency}")
    except Exception as exc:
        print(f"[ERROR] Error setting frequency: {exc}")
    sys.exit(1)

if __name__ == "__main__":
    main()
