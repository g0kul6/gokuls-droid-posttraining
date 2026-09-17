#!/usr/bin/env python3
"""Create a deterministic archive of the built static website."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import tarfile
from pathlib import Path


def normalized(info: tarfile.TarInfo) -> tarfile.TarInfo:
    info.uid = 0
    info.gid = 0
    info.uname = ""
    info.gname = ""
    info.mtime = 0
    return info


def package(build_dir: Path, output_dir: Path) -> tuple[Path, str]:
    if not (build_dir / "index.html").is_file():
        raise SystemExit(f"missing static build: {build_dir / 'index.html'}")
    output_dir.mkdir(parents=True, exist_ok=True)
    archive = output_dir / "gokuls-droid-posttraining-site.tar.gz"
    with open(archive, "wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as zipped:
            with tarfile.open(mode="w", fileobj=zipped) as tar:
                for path in sorted(build_dir.rglob("*")):
                    tar.add(
                        path,
                        arcname=Path("gokuls-droid-posttraining-site")
                        / path.relative_to(build_dir),
                        recursive=False,
                        filter=normalized,
                    )
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    checksum = archive.with_suffix(archive.suffix + ".sha256")
    checksum.write_text(f"{digest}  {archive.name}\n", encoding="utf-8")
    return archive, digest


def main() -> None:
    parser = argparse.ArgumentParser()
    root = Path(__file__).resolve().parents[1]
    parser.add_argument("--build-dir", type=Path, default=root / "_build/html")
    parser.add_argument("--output-dir", type=Path, default=root / "_dist")
    args = parser.parse_args()
    archive, digest = package(
        args.build_dir.resolve(), args.output_dir.resolve()
    )
    print(f"Packaged {archive}")
    print(f"SHA256 {digest}")


if __name__ == "__main__":
    main()
