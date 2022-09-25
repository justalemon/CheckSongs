import hashlib
import sys
from pathlib import Path


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
            if len(existing) == 2: # if we now have 2
                print(f"Found duplicated file: {existing[0].absolute()} ({sha256_hash})")

            print(f"Found duplicated file: {existing[-1].absolute()} ({sha256_hash})")

        known_hashes[sha256_hash] = existing


if __name__ == "__main__":
    main()
