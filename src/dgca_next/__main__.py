"""Administrative CLI only; no engine command is exposed."""

import argparse
import sys
from pathlib import Path

from dgca_next import __version__
from dgca_next.integrity import SpecIntegrityError, verify_specs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="dgca-next", description=__doc__)
    parser.add_argument("--version", action="version", version=f"dgca-next {__version__}")
    commands = parser.add_subparsers(dest="command", required=True)
    verify = commands.add_parser("verify-specs", help="verify raw repository scientific sources")
    verify.add_argument("--repo-root", type=Path, default=Path.cwd())
    args = parser.parse_args(argv)
    try:
        results = verify_specs(args.repo_root)
    except SpecIntegrityError as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 1
    print("\n".join(results))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
