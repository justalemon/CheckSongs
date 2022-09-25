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


def get_song_info(path: Path):
    info = SONG_INFO_CACHE.get(path, None)

    if info is None:
        try:
            with open(path, "r") as file:
                parsed = json.load(file)
            info = SongInformation(parsed)
        except Exception:
            info = EMPTY_INFORMATION
        print(f"{info.name} ({info.sub_name}) - {info.song_author} [{info.level_author}]")
        SONG_INFO_CACHE[path] = info

    return info


def print_song_duplicate(path: Path, sha256_hash: str):
    print(f"\tDuplicated file: {path.absolute()} ({sha256_hash})")


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
            if len(existing) == 2:  # if we now have 2
                print_song_duplicate(existing[0], sha256_hash)

            print_song_duplicate(existing[-1], sha256_hash)

        known_hashes[sha256_hash] = existing


if __name__ == "__main__":
    main()
