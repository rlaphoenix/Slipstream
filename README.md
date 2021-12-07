# Slipstream

![Preview](docs/images/preview.png)

*<small>Preview as of December 2021</small>*

* * *

[![Pull requests welcome](https://img.shields.io/badge/PRs-welcome-brightgreen)](http://makeapullrequest.com)
[![GPLv3 license](https://img.shields.io/badge/license-GPLv3-blue)](https://github.com/rlaPHOENiX/Slipstream/blob/master/LICENSE)
[![PyPI version](https://img.shields.io/pypi/v/pslipstream)](https://pypi.python.org/pypi/pslipstream)
[![Python versions](https://img.shields.io/pypi/pyversions/pslipstream)](https://pypi.python.org/pypi/pslipstream)
[![PyPI status](https://img.shields.io/pypi/status/pslipstream)](https://pypi.python.org/pypi/pslipstream)
[![Contributors](https://img.shields.io/github/contributors/rlaPHOENiX/Slipstream)](https://github.com/rlaPHOENiX/Slipstream/graphs/contributors)
[![GitHub issues](https://img.shields.io/github/issues/rlaPHOENiX/Slipstream)](https://github.com/rlaPHOENiX/Slipstream/issues)
![Build](https://github.com/rlaPHOENiX/Slipstream/workflows/Build/badge.svg?branch=master)

Slipstream's goal is to provide the user's a dead-simple process for backing up their legally owned home-media to a
wide array of formats, including a full backup. Slipstream can be used with it's GUI, as CLI, or as an importable
package.

It's trying to be different from the other solutions out there by providing as much information about the home-media
as one could need while being stupid simple to use.

## Call for designers

This project is looking for a Logo, Icon, and Banner artwork. If you have some free time and would like to contribute
one (or all :O) to this project, please do!

Not begging for a billion-dollar design, just something unique that shows off the project well.

## Quick Installation

    python -m pip install --user pslipstream

If you wish to manually install from the source, take a look at [Building](#building-source-and-wheel-distributions).

## To-do

- [X] Craft GUI with Qt.
- [x] Create a file based settings system.
- [x] Add drive selection option.
- [X] Add Linux support to the drive selection option.
- [X] Add DVD backup support, using libdvdcss.
- [X] Add information window with details about the DVD ISO.
- [x] Write PyInstaller spec file.
- [ ] Add information window with details about the DVD-Video data, like Layer count, titles, languages, subtitles, codecs, e.t.c.
- [ ] Add support for remuxing to Matroska Video (MKV) with MKVToolnix.
- [ ] Add the ability to choose to remux by Title ID's.
- [ ] Add the ability to choose to remux by VOB ID, and VOB CELL's.
- [ ] Add the ability to choose which tracks of a title to output rather than all available.
- [ ] Add Blu-ray backup support, using libaacs.

## Usage

To run Slipstream, type `pslipstream` into Terminal, App Launcher, or Start Menu.

## Working with the Source Code

This project requires [Poetry], so feel free to take advantage and use it for its various conveniences like
building sdist/wheel packages, creating and managing dependencies, virtual environments, and more.

Note:

- Source Code may have changes that may be old, not yet tested or stable, or may have regressions.
- Only run or install from Source Code if you have a good reason. Examples would be to test for regressions, test
  changes (either your own or other contributors), or to research the code (agreeing to the [LICENSE](LICENSE)).
- [Poetry] is required as it's used as the [PEP 517] build system, virtual environment manager, dependency manager,
  and more.

  [Poetry]: <https://python-poetry.org/docs/#installation>
  [PEP 517]: <https://www.python.org/dev/peps/pep-0517>

### Install from Source Code

    git clone https://github.com/rlaPHOENiX/Slipstream.git
    cd Slipstream
    python -m pip install --user .

### Building source and wheel distributions

    poetry build

You can specify `-f` to build `sdist` or `wheel` only. Built files can be found in the `/dist` directory.

### Packing with PyInstaller

    python -m pip install --user pyinstaller
    poetry run pyinstaller Slipstream.spec
    .\dist\Slipstream.exe

Feel free to apply any CLI options/switches you feel like, see `pyinstaller -h`.
