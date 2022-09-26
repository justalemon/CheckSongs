import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Optional, Union


RE_FOLDER_NAME = re.compile("[A-Za-z0-9]{1,6} \(.{1,} - .{1,}\)")


class SongInformation:
    def __init__(self, path: Optional[Path]):
        self.levels: dict[str, Path] = {}
        self.has_been_loaded: bool = False
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

                self.has_been_loaded = True
            except Exception as e:
                self.exception = e

        self.name = info.get("_songName", "Unknown Song Name")
        self.sub_name = info.get("_songSubName", "No Sub Name")
        self.song_author = info.get("_songAuthorName", "Unknown Song Author")
        self.level_author = info.get("_levelAuthorName", "Unknown Level Author")
        self.hash: str = hashlib.sha1(contents).hexdigest()

    def __str__(self):
        return f"{self.name} ({self.sub_name}) - {self.song_author} [{self.level_author}] @ {self.path}"

    @property
    def is_valid(self):
        return self.has_been_loaded and self.path is not None and self.is_folder_name_valid

    @property
    def is_folder_name_valid(self):
        if self.path is None:
            return False

        return RE_FOLDER_NAME.fullmatch(self.path.name) is not None


EMPTY_INFORMATION = SongInformation(None)
SONG_INFO_CACHE: dict[Path, SongInformation] = {}


def get_song_info(path: Path):
    info = SONG_INFO_CACHE.get(path, None)

    if info is None:
        info = SongInformation(path)
        SONG_INFO_CACHE[path] = info

    return info


def main():
    if len(sys.argv) < 2:
        songs_folder = Path(".") / "Beat Saber_Data" / "CustomLevels"

        if not songs_folder.exists():
            print("Current folder is not a Beat Saber folder!\n"
                  "You can move this file to the Beat Saber install directory or explicitly specify it "
                  "in the command line.")
            input()
            sys.exit(1)
    else:
        songs_folder = Path(sys.argv[1])

    songs: list[SongInformation] = []
    hashes: dict[str, list[Union[Path, SongInformation]]] = {}

    print("Checking songs, please wait...")

    for path in songs_folder.iterdir():
        info = get_song_info(path)
        to = sys.stdout if info.is_valid else sys.stderr

        print(info, file=to)
        if info.exception is not None:
            print(f"\tInvalid Metadata: {type(info.exception)} - {info.exception}", file=sys.stderr)

        existing_song = hashes.get(info.hash, [])
        existing_song.append(info)
        songs.append(info)

        if len(existing_song) > 1:  # if there is more than one
            print(f"\tFound duplicated song: {info}", file=sys.stderr)
        if info.path is not None and not info.is_folder_name_valid:
            print(f"\tFolder name '{info.path.name}' is not valid", file=sys.stderr)

        hashes[info.hash] = existing_song

    def check(x: str):
        return hashes[x][0].name

    known_duplicates = {x: hashes[x] for x in sorted(hashes.keys(), key=check) if len(hashes[x]) > 1}
    known_invalid_names = [x for x in songs if not x.is_folder_name_valid]

    with open("what_we_found.txt", "w", encoding="utf-8") as file:
        print("\nDuplicates Found:\n", file=sys.stdout)
        print("Duplicates Found:\n", file=file)

        for sha_hash, matches in known_duplicates.items():
            print(sha_hash, file=sys.stderr)
            print(sha_hash, file=file)

            for match in matches:
                print(f"\t{match}", file=sys.stderr)
                print(f"\t{match}", file=file)

        print("\nInvalid Names found:\n", file=sys.stdout)
        print("\nInvalid Names found:\n", file=file)

        for song in known_invalid_names:
            print(f"\t{song.path.name} ({song.hash})", file=sys.stderr)
            print(f"\t{song.path.name} ({song.hash})", file=file)


if __name__ == "__main__":
    main()
