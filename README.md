<p>&nbsp;</p><p>&nbsp;</p>

<p align="center"><strong>Slipstream</strong> is the most informative Home-media backup solution.</p>

<p>&nbsp;</p><p>&nbsp;</p>

---

<p>&nbsp;</p><p>&nbsp;</p>

Slipstream's goal is to provide the user's a dead-simple process for backing up their legally owned home-media to a wide array of formats, including a full backup. Slipstream can be used with it's GUI, as CLI, or as an importable package. It's trying to be different from the other solutions out there by providing as much information about the home-media as one could need while being stupid simple to use.

<p>&nbsp;</p><p>&nbsp;</p>

<span align="center">

[![Pull requests welcome](https://img.shields.io/badge/PRs-welcome-brightgreen)](http://makeapullrequest.com)
[![GPLv3 license](https://img.shields.io/badge/license-GPLv3-blue)](https://github.com/rlaPHOENiX/Slipstream/blob/master/LICENSE)
[![PyPI version](https://img.shields.io/pypi/v/pslipstream)](https://pypi.python.org/pypi/pslipstream)
[![Python versions](https://img.shields.io/pypi/pyversions/pslipstream)](https://pypi.python.org/pypi/pslipstream)
[![PyPI status](https://img.shields.io/pypi/status/pslipstream)](https://pypi.python.org/pypi/pslipstream)
[![Contributors](https://img.shields.io/github/contributors/rlaPHOENiX/Slipstream)](https://github.com/rlaPHOENiX/Slipstream/graphs/contributors)
[![GitHub issues](https://img.shields.io/github/issues/rlaPHOENiX/Slipstream)](https://github.com/rlaPHOENiX/Slipstream/issues)
![Build](https://github.com/rlaPHOENiX/Slipstream/workflows/Build/badge.svg?branch=master)

[![Support me on ko-fi](https://www.ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/W7W01KX2G)

</span>

<p>&nbsp;</p><p>&nbsp;</p>

# Call for designers

This project is looking for a Logo, Icon, and Banner artwork. If you have some free time and would like to contribute one (or all :O) to this project, please do!  
Not begging for a billion-dollar design, just something unique that shows off the project well.

<p>&nbsp;</p><p>&nbsp;</p>

# Quick Installation

    python -m pip install --user pslipstream

If you wish to manually install from the source, take a look at [Building](#building) below.

<p>&nbsp;</p><p>&nbsp;</p>

# To-do

- [x] Craft GUI with Chromium Embedded Framework (CEF).
- [x] Create a file based settings system.
- [x] Implement a quick and simple way to build, pack with PyInstaller, upload, and install.
- [x] Add DVD backup support, using libdvdcss.
- [x] Implement the UI and bridge the Javascript and Python together.
- [x] Add drive selection option with information about the drive including disc label.
- [x] Add information window with details about the DVD ISO.
- [ ] Add information window with details about the DVD-Video data, like Layer count, titles, languages, subtitles, codecs, e.t.c.
- [ ] Add support for remuxing to Matroka Video (MKV) with MkvToolnix.
- [ ] Add the ability to choose to remux by Title ID's.
- [ ] Add the ability to choose to remux by VOB ID, and VOB CELL's.
- [ ] Add the ability to choose which tracks of a title to output rather than all available.
- [ ] Add Blu-ray backup support, using libaacs.

<p>&nbsp;</p><p>&nbsp;</p>

# Usage

To run Slipstream, type `pslipstream` into Terminal, App Launcher, or Start Menu.

<p>&nbsp;</p><p>&nbsp;</p>

## Building

    git clone https://github.com/rlaPHOENiX/Slipstream.git
    cd Slipstream

> Note:

Now you have three options, `dist`, `pack`, or `install`:

- `dist`, Build the source into a package file that's shareable and installable with pip, will be in /dist:  
  `python setup.py dist`
- `pack`, Build and pack the source with PyInstaller, resulting in a single portable binary file, will be in /dist:  
  `python -m pip install PyInstaller`  
  `python setup.py pack`
- `install`, Build the source and install it with pip, essentially the same result as [Quick Installation](#installation) but without PyPI.org:  
  `python -m pip install --user .`

Once built, use it as you please. If you went the `install` route, follow [Usage](#usage).
