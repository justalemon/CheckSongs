import hashlib
import json
import sys
from pathlib import Path


class SongInformation:
    def __init__(self, data: dict):
        self.name = data.get("_songName", "Unknown Song Name")
        self.sub_name = data.get("_songSubName", "No Sub Name")
        self.song_author = data.get("_songAuthorName", "Unknown Song Author")
        self.level_author = data.get("_levelAuthorName", "Unknown Level Author")


EMPTY_INFORMATION = SongInformation({})
SONG_INFO_CACHE: dict[Path, SongInformation] = {}


def print_song_duplicate(path: Path, sha256_hash: str):
    info_path = path.with_name("info.dat")
    info = SONG_INFO_CACHE.get(info_path, None)

    if info is None:
        try:
            with open(info_path, "r") as file:
                parsed = json.load(file)
            info = SongInformation(parsed)
        except Exception:
            info = EMPTY_INFORMATION
        SONG_INFO_CACHE[info_path] = info

    print(f"{info.name} ({info.sub_name}) - {info.song_author} [{info.level_author}]")
    print(f"\tDuplicated file: {path.absolute()} ({sha256_hash})")


def main():
    if len(sys.argv) < 2:
        sys.exit("Usage: check_songs.py [path]")

    known_hashes: dict[str, list[Path]] = {}

    for path in Path(sys.argv[1]).rglob("*.dat"):
        with open(path, "rb") as file:
            contents = file.read()
            sha256_hash = hashlib.sha256(contents).hexdigest()

        existing = known_hashes.get(sha256_hash, [])
        existing.append(path)

        if len(existing) > 1:  # if there is more than one
            if len(existing) == 2:  # if we now have 2
                print_song_duplicate(existing[0], sha256_hash)

            print_song_duplicate(existing[-1], sha256_hash)

        known_hashes[sha256_hash] = existing


if __name__ == "__main__":
    main()
