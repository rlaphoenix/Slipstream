![Banner](assets/banner.png)

[![License](https://img.shields.io/:license-GPL%203.0-blue.svg)](https://github.com/rlaphoenix/slipstream/blob/master/LICENSE)
[![Python version](https://img.shields.io/badge/python-3.11%2B-informational)](https://www.python.org/)
[![Manager: uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/Onyx-Nostalgia/uv/refs/heads/fix/logo-badge/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Linter: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Build status](https://github.com/rlaphoenix/slipstream/actions/workflows/ci.yml/badge.svg?branch=master)](https://github.com/rlaphoenix/slipstream/actions/workflows/ci.yml)

Slipstream's goal is to provide the user's a dead-simple process for backing up their legally owned home-media to a
wide array of formats, including a full backup. Slipstream is a desktop GUI application.

It's trying to be different from the other solutions out there by providing as much information about the home-media
as one could need while being stupid simple to use.

![Preview](assets/preview.png)

## Installation

*Windows Installers and a portable executable are available on the [Releases] page.*

Download the latest installer, run it, then launch Slipstream from the Start Menu or Desktop shortcut.
Prefer not to install? Grab the portable `.exe` from the same page and run it directly.

  [Releases]: <https://github.com/rlaphoenix/slipstream/releases>

## To-do

- [X] Craft GUI with Qt.
- [x] Create a file based settings system.
- [x] Add drive selection option.
- [X] Add DVD backup support, using libdvdcss.
- [X] Add information window with details about the DVD ISO.
- [x] Write PyInstaller spec file.
- [ ] Add information window with details about the DVD-Video data, like Layer count, titles, languages, subtitles, codecs, e.t.c.
- [ ] Add support for remuxing to Matroska Video (MKV) with MKVToolnix.
- [ ] Add the ability to choose to remux by Title ID's.
- [ ] Add the ability to choose to remux by VOB ID, and VOB CELL's.
- [ ] Add the ability to choose which tracks of a title to output rather than all available.
- [ ] Add Blu-ray backup support, using libaacs.

## Licensing

This software is licensed under the terms of [GNU General Public License, Version 3.0](LICENSE).  
You can find a copy of the license in the LICENSE file in the root folder.

- [Music disc icons created by Freepik - Flaticon](https://www.flaticon.com/free-icons/music-disc)
- [Info icons created by Freepik - Flaticon](https://www.flaticon.com/free-icons/info)
- [Refresh icons created by Pixel perfect - Flaticon](https://www.flaticon.com/free-icons/refresh)

* * *

© rlaphoenix 2020-2023
