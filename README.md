# Slipstream

The most informative Home-media backup solution.  
Slipstream is a home-media REMUX-ing and backup software with a wide array of features.

<p align="center">
<a href="https://python.org"><img src="https://img.shields.io/badge/python-3.7%2B-informational?style=flat-square" /></a>
<a href="https://github.com/rlaPHOENiX/Slipstream/blob/master/LICENSE"><img alt="license" src="https://img.shields.io/github/license/rlaPHOENiX/Slipstream?style=flat-square" /></a>
<a href="https://github.com/rlaPHOENiX/Slipstream/issues"><img alt="issues" src="https://img.shields.io/github/issues/rlaPHOENiX/Slipstream?style=flat-square" /></a>
<a href="http://makeapullrequest.com"><img alt="pr's welcome" src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square" /></a>
<br>
<a href="https://ko-fi.com/W7W01KX2G"><img alt="support me" src="https://www.ko-fi.com/img/githubbutton_sm.svg" /></a>
</p>

## To-do

- [X] Craft GUI with Chromium Embedded Framework (CEF).
- [X] Create a file based settings system.
- [X] Implement a quick and simple way to build, pack with PyInstaller, upload, and install.
- [X] Add DVD backup support, using libdvdcss.
- [X] Implement the UI and bridge the Javascript and Python together.
- [X] Add drive selection option with information about the drive including disc label.
- [X] Add information window with details about the DVD ISO.
- [ ] Add information window with details about the DVD-Video data, like Layer count, titles, languages, subtitles, codecs, e.t.c.
- [ ] Add support for remuxing to Matroka Video (MKV) with MkvToolnix.
- [ ] Add the ability to choose to remux by Title ID's.
- [ ] Add the ability to choose to remux by VOB ID, and VOB CELL's.
- [ ] Add the ability to choose which tracks of a title to output rather than all available.
- [ ] Add Blu-ray backup support, using libaacs.

## Quick Installation

    python -m pip install --user slipstream

If you wish to manually install from source, take a look at [Building](#building) below.

## Usage

To run Slipstream, type `slipstream` into Terminal, App Launcher, or Start Menu.

## Building

> Note:
> Make sure you use Python version 3.x (`python --version`). Some environments may use `python` for Python version 2.x and `python3` for Python version 3.x so make sure you use the right one from here on in all the following build commands.

    git clone https://github.com/rlaPHOENiX/Slipstream.git
    cd Slipstream

Now you have three options, `dist`, `pack`, or `install`:

- `dist`, Build the source into a package file that's shareable and installable with pip, will be in /dist:  
  `python setup.py dist`
- `pack`, Build and pack the source with PyInstaller, resulting in a single portable binary file, will be in /dist:  
  `python setup.py pack`
- `install`, Build the source and install it with pip, essentially the same result as [Quick Installation](#installation) but without PyPI.org:  
  `python -m pip install --user .`

Once built, use it as you please. If you went the `install` route, follow [Usage](#usage).