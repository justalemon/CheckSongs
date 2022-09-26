# Song Checker for Beat Saber<br>[![GitHub Actions][actions-img]][actions-url]

This is a simple script that will check your Beat Saber songs and try to identify duplicated songs and songs where the folder name does not matches the common format of `[ID] ([Song Name] - [Level Author])`.

Special thanks to this kind people from the Beat Saber Modding Group Discord:

* Kinsi, Shadnix and Fern for helping me with the SHA1 hashing of the levels
* Top_Cat, Kinsi and Shadnix for help with the [beatsaver.com API](https://api.beatsaver.com/docs)
* Top_Cat for showing me where how the song folder names are formatted

## Download

* [GitHub Actions](https://nightly.link/justalemon/CheckSongs/workflows/main/master/CheckSongs.zip)

## Installation

Open the compressed file and extract the file called `CheckSongs.exe` to your Beat Saber folder.

## Usage

Double click `CheckSongs.exe` and it will start comparing your songs. It's that easy.

After it finishes, you will see a list of songs that are duplicated and another list of songs that has the wrong folder format. The lists will also be saved to a file called `what_we_found.txt`. 

[actions-img]: https://img.shields.io/github/workflow/status/justalemon/CheckSongs/Compile%20Script?label=github%20actions
[actions-url]: https://github.com/justalemon/CheckSongs/actions
