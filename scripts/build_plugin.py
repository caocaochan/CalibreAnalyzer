from __future__ import annotations

import argparse
import os
import re
import shutil
import tempfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN_NAME = "ChineseCharacterAnalyzer-Calibre-Plugin"
FILES_TO_PACKAGE = [
    "__init__.py",
    "analyzer.py",
    "anki_connect.py",
    "anki_parser.py",
    "dialog.py",
    "hsk_data.py",
    "runtime_manager.py",
    "ui.py",
    "plugin-import-name-chinese_character_analyzer.txt",
    "New-HSK-Vocabulary-Level-1.txt",
    "New-HSK-Vocabulary-Level-2.txt",
    "New-HSK-Vocabulary-Level-3.txt",
    "New-HSK-Vocabulary-Level-4.txt",
    "New-HSK-Vocabulary-Level-5.txt",
    "New-HSK-Vocabulary-Level-6.txt",
    "New-HSK-Vocabulary-Level-7-9.txt",
    "images",
    "runtime_assets",
]
VERSION_RE = re.compile(r"^(\d{4})\.(\d{2})\.(\d{2})\.(\d+)$")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", required=True, help="Release version like YYYY.MM.DD.X")
    parser.add_argument(
        "--output-dir",
        default=str(ROOT / "dist"),
        help="Directory to write build artifacts into",
    )
    return parser.parse_args()


def validate_version(version: str):
    match = VERSION_RE.match(version)
    if not match:
        raise SystemExit(f"Invalid version '{version}'. Expected YYYY.MM.DD.X")
    return tuple(int(part) for part in match.groups())


def patch_init_version(init_path: Path, version_tuple):
    text = init_path.read_text(encoding="utf-8")
    replacement = f"version = ({version_tuple[0]}, {version_tuple[1]}, {version_tuple[2]}, {version_tuple[3]})"
    patched, count = re.subn(
        r"version = \(\d+, \d+, \d+(?:, \d+)?\)",
        replacement,
        text,
        count=1,
    )
    if count != 1:
        raise SystemExit("Could not patch plugin version in __init__.py")
    init_path.write_text(patched, encoding="utf-8")


def copy_tree(src: Path, dst: Path):
    if src.is_dir():
        shutil.copytree(src, dst)
    else:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def build_zip(staging_dir: Path, zip_path: Path):
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path in sorted(staging_dir.rglob("*")):
            if path.is_file():
                zf.write(path, path.relative_to(staging_dir))


def main():
    args = parse_args()
    version_tuple = validate_version(args.version)
    output_dir = Path(args.output_dir)

    with tempfile.TemporaryDirectory(prefix="cca-build-") as temp_dir:
        staging_dir = Path(temp_dir) / "staging"
        staging_dir.mkdir(parents=True)

        for relative in FILES_TO_PACKAGE:
            copy_tree(ROOT / relative, staging_dir / relative)

        patch_init_version(staging_dir / "__init__.py", version_tuple)

        versioned_zip = output_dir / f"{PLUGIN_NAME}-v{args.version}.zip"
        generic_zip = output_dir / f"{PLUGIN_NAME}.zip"
        build_zip(staging_dir, versioned_zip)
        shutil.copy2(versioned_zip, generic_zip)

        print(versioned_zip)
        print(generic_zip)


if __name__ == "__main__":
    main()
