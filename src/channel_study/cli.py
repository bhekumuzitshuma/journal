"""Command-line entry point for the study scaffold."""

import argparse
import json
from pathlib import Path

from .fingerprint import jpeg_fingerprint


def main() -> None:
    parser = argparse.ArgumentParser(description="Messaging-channel reliability study tools")
    subparsers = parser.add_subparsers(dest="command", required=True)

    fingerprint_parser = subparsers.add_parser("fingerprint", help="fingerprint one JPEG")
    fingerprint_parser.add_argument("image", type=Path)
    args = parser.parse_args()

    if args.command == "fingerprint":
        print(json.dumps(jpeg_fingerprint(args.image), indent=2))


if __name__ == "__main__":
    main()
