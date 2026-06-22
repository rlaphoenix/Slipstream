# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Added

- A configurable optical drive read speed (Settings -> "Drive read speed"), requested from the drive
  via SCSI SET STREAMING when a disc is loaded. Set as a DVD speed multiplier (e.g. 6x; 1x = 1385
  KB/s), defaulting to 6x; 0 leaves the drive at its own default. Drives may ignore or cap it (notably
  firmware riplock on DVD-Video), so it is best-effort.

### Changed

- Updated pydvdcss to 1.5.0.
- libdvdcss is now provided by the pydvdcss package, which bundles it in its Windows wheels;
  Slipstream no longer vendors its own libdvdcss DLL.

## [1.0.1] - 2026-06-20

### Changed

- Switched project management from Poetry to uv.
- Raised the minimum supported Python version to 3.11.
- Updated all dependencies to their latest versions, including the bundled libdvdcss to 1.5.0.

### Removed

- The command-line interface and the pip/PyPI-installable package. Slipstream is distributed only as a
  Windows installer and portable executable.

### Fixed

- Backing up a disc in the GUI no longer crashes in the windowed build (tqdm writing to an absent console).
- Loading a disc no longer intermittently fails with "Expected at least 2 UDF Anchors"; opening the disc in
  pycdlib is now retried.
- Backing up a disc no longer fails near the end when the disc returns fewer sectors than its volume
  descriptor declares; the unreadable trailing padding is zero-filled so the image keeps its full size.
- libdvdcss is now located correctly when running from source.

## [1.0.0] - 2023-10-12

New Beginnings - Initial release with a consistent and coherent project structure.  
Previous 0.x releases have been yanked and history has been rewritten to slim the repo commit count.

[1.0.1]: https://github.com/Homemediadb/Slipstream/releases/tag/v1.0.1
[1.0.0]: https://github.com/Homemediadb/Slipstream/releases/tag/v1.0.0
