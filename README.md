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
- [ ] Design the UI.
- [ ] Implement the UI and bridge the Javascript and Python together.
- [ ] Add drive selection dropdown with information about the drive including disc label.
- [ ] Add information window with details about the DVD.
- [ ] Add DVD backup support, perhaps using libdvdcss?
- [ ] Add support for remuxing to Matroka Video (MKV) with MkvToolnix.
- [ ] Add the ability to choose to remux by Title ID's.
- [ ] Add the ability to choose to remux by VOB ID, and VOB CELL's.
- [ ] Add the ability to choose which tracks of a title to output rather than all available.

## Building

### Note:

- Make sure you use Python version 3.x (`python --version`). Some environments may use `python` for Python version 2.x and `python3` for Python version 3.x so make sure you use the right one from here on in all the following build commands.

### Method 1: PyInstaller (Portable executable file)

This method builds Slipstream to a single executable file with no dependencies whatsoever. A fully portable binary.

```
git clone https://github.com/rlaPHOENiX/Slipstream.git
cd Slipstream
pyinstaller -F "Slipstream/__init__.py" --add-data "Slipstream/static:static" --add-data "Slipstream/cefpython3:cefpython3" --hidden-import="pkg_resources.py2_warn" -n "Slipstream"
ls dist
```

The built executable will be found in the `dist/` folder. You can move the executable anywhere you wish as it is entirely portable. You won't even need python installed to use it. You may need to explicitly give it execute permission (`chmod +x`).

### Method 2: PIP Python package file (setuptools/wheel)

This method builds Slipstream into a wheel package file that can be installed by tools like Python's PIP.

```
python -m pip install --user --upgrade setuptools wheel
python setup.py sdist bdist_wheel
```

The built package files will be found in the `dist/` folder. It can be installed with `python -m pip install --user .`. Once installed, it can be run by typing `slipstream` in terminal.
