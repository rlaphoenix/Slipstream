# Release History

## master

**Improvements**

- Add version to window title.

**Bug fixes**

- Reset the progress bar on Dvd dispose.

## 0.1.6

**Bug fixes**

- Update two old `g.PROG` references to `g.PROGRESS` references.
- Properly filter "disk" devices from device list helper.

## 0.1.5

**Bug fixes**

- Deal with `main()`'s metadata preparation BEFORE dealing with global variables, as meta is used in the globals.

## 0.1.4

**Bug fixes**

- Move `setup_commands/pack.py`'s PyInstaller imports to inside the `run()` function, so it only attempts the import if the pack command is used.

## 0.1.3

**Bug fixes**

- Move `pslipstream.__version__` to `meta.py` so that `setup.py` doesn't try and import the entire pslipstream module.

## 0.1.2

**Improvements**

- Huge code cleanup throughout the entire repository.
- Remove a bunch of unnecessary GUI related calls and code.
- Remove unnecessary PyInstaller call in the release github workflow.
- Added instructions (one-liner change) on supporting `cefpython3` for python 3.8. It will show the instructions when it detects it failed the import.

**Bug fixes**

- Fix setup.py pack, move PyInstall imports from start of setup.py to inside PackCommand class, get folder name from `__title_pkg__` meta
- Move the need to import appdirs and cefpython3 in `__version__.py` to `__init__.main()` since its used by setup.py, causing a circular dependency
- Add pydvdid to requirements via `dependency_links` allowing it to auto install pydvdid>1.1 (my fork)
- Change build github workflow to use Py 3.7 as cefpython3 doesn't have proper support for 3.8 yet. It can run on Python 3.8, but you need to make a one line edit to it, which I don't know a correct way of doing that with Github Actions.

## 0.1.1

**Bug fixes**

- Fix and add a checksum check to --license to ensure it loads correctly or not at all.
- Fix a problem with devicelist that caused it to get the device list every render.

**Improvements**
- Clear various React, Lint, and GatsbyJS warning messages about CSS, JSX, Best Practices and what not.
- Add --dev argument, which is just a helpful switch for testing, not aimed for user use.

**Misc**
- Remove unnecessary GUI bridge/ui-handler files as they are no longer used.
- This removed some angularjs 1.x code that was accidentally being ran on DOM ready too (whoops).
- Update development status trove from 2 (Pre-Alpha) to 3 (Alpha).

## 0.1.0

- Initial GUI, Library and Console Code.
- Support for DVD's and the ability to make a full decrypted backup with libdvdcss.
- Very basic overall but with great aspirations in mind!
