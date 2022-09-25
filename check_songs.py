import hashlib
import json
import sys
from pathlib import Path
from typing import Optional, Union


class SongInformation:
    def __init__(self, path: Optional[Path]):
        self.levels: dict[str, Path] = {}
        self.valid: bool = False
        self.exception: Optional[Exception] = None
        self.path: Optional[Path] = path

        info = {}
        contents = b""

        if path is not None:
            try:
                info_path = path / "info.dat"

                with open(info_path, "rb") as file:
                    contents = file.read()

                info = json.loads(contents.decode("utf-8"))

                for map_set in info["_difficultyBeatmapSets"]:
                    for difficulty in map_set["_difficultyBeatmaps"]:
                        filename = difficulty["_beatmapFilename"]

                        with open(path / filename, "rb") as file:
                            map_data = file.read()

                        map_hash = hashlib.sha1(map_data).hexdigest()
                        self.levels[map_hash] = filename
                        contents += map_data

                self.valid = True
            except Exception as e:
                self.exception = e

        self.name = info.get("_songName", "Unknown Song Name")
        self.sub_name = info.get("_songSubName", "No Sub Name")
        self.song_author = info.get("_songAuthorName", "Unknown Song Author")
        self.level_author = info.get("_levelAuthorName", "Unknown Level Author")
        self.hash: str = hashlib.sha1(contents).hexdigest()

    def __str__(self):
        return f"{self.name} ({self.sub_name}) - {self.song_author} [{self.level_author}] @ {self.path}"


EMPTY_INFORMATION = SongInformation(None)
SONG_INFO_CACHE: dict[Path, SongInformation] = {}


def get_song_info(path: Path):
    info = SONG_INFO_CACHE.get(path, None)

    if info is None:
        info = SongInformation(path)
        to = sys.stdout if info.exception is None else sys.stderr

        print(info, file=to)
        if info.exception is not None:
            print(f"\tInvalid Metadata: {type(info.exception)} - {info.exception}", file=sys.stderr)

        SONG_INFO_CACHE[path] = info

    return info


def print_song_duplicate(path: Path, sha256_hash: str):
    print(f"\tDuplicated file: {path.absolute()} ({sha256_hash})", file=sys.stderr)


def main():
    if len(sys.argv) < 2:
        sys.exit("Usage: check_songs.py [path]")

    known_hashes: dict[str, list[Union[Path, SongInformation]]] = {}

    for path in Path(sys.argv[1]).iterdir():
        info = get_song_info(path)

        existing_song = known_hashes.get(info.hash, [])
        existing_song.append(info)

        if len(existing_song) > 1:  # if there is more than one
            print(f"\tFound duplicated song: {info}", file=sys.stderr)

        known_hashes[info.hash] = existing_song

    known_duplicates = {k: v for k, v in known_hashes.items() if len(v) > 1}

    if known_duplicates:
        print("\nFound Duplicates:\n", file=sys.stderr)

        for sha256_hash, matches in known_duplicates.items():
            print(sha256_hash, file=sys.stderr)

            for match in matches:
                print(f"\t{match}", file=sys.stderr)


if __name__ == "__main__":
    main()
