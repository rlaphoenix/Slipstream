# Release History

## master

N/A

## 0.1.1

**Bugfixes**

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
