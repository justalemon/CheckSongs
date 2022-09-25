import hashlib
import json
import sys
from pathlib import Path
from typing import Optional


class SongInformation:
    def __init__(self, data: dict):
        self.name = data.get("_songName", "Unknown Song Name")
        self.sub_name = data.get("_songSubName", "No Sub Name")
        self.song_author = data.get("_songAuthorName", "Unknown Song Author")
        self.level_author = data.get("_levelAuthorName", "Unknown Level Author")


EMPTY_INFORMATION = SongInformation({})
SONG_INFO_CACHE: dict[Path, SongInformation] = {}


def get_song_info(path: Path):
    info = SONG_INFO_CACHE.get(path, None)

    if info is None:
        error: Optional[Exception] = None

        try:
            with open(path, "r", encoding="utf-8") as file:
                parsed = json.load(file)
            info = SongInformation(parsed)
            to = sys.stdout
        except Exception as e:
            info = EMPTY_INFORMATION
            to = sys.stderr
            error = e

        print(f"{info.name} ({info.sub_name}) - {info.song_author} [{info.level_author}] @ {path.parent}", file=to)

        if error is not None:
            print(f"\tInvalid Metadata: {type(error)} - {error}", file=sys.stderr)

        SONG_INFO_CACHE[path] = info

    return info


def print_song_duplicate(path: Path, sha256_hash: str):
    print(f"\tDuplicated file: {path.absolute()} ({sha256_hash})", file=sys.stderr)


def main():
    if len(sys.argv) < 2:
        sys.exit("Usage: check_songs.py [path]")

    known_hashes: dict[str, list[Path]] = {}

    for path in Path(sys.argv[1]).rglob("*.dat"):
        info_path = path.with_name("info.dat")
        get_song_info(info_path)

        with open(path, "rb") as file:
            contents = file.read()
            sha256_hash = hashlib.sha256(contents).hexdigest()

        existing = known_hashes.get(sha256_hash, [])
        existing.append(path)

        if len(existing) > 1:  # if there is more than one
            print(f"\tFound duplicated file: {path.name}", file=sys.stderr)

        known_hashes[sha256_hash] = existing

    known_duplicates = {k: v for k, v in known_hashes.items() if len(v) > 1}

    if known_duplicates:
        print("\nFound Duplicates:\n", file=sys.stderr)

        for sha256_hash, matches in known_duplicates.items():
            print(sha256_hash, file=sys.stderr)

            for match in matches:
                print(f"\t{match}", file=sys.stderr)


if __name__ == "__main__":
    main()
