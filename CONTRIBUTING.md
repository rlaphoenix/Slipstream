# Development

This project is managed using [uv](https://docs.astral.sh/uv), an extremely fast Python package and project manager.
Install the latest version of uv before continuing. Development currently requires Python 3.11+.

## Set up

Starting from Zero? Not sure where to begin? Here's steps on setting up this Python project using uv. Note that
uv installation instructions should be followed from the uv Docs: https://docs.astral.sh/uv/getting-started/installation

1. Clone the Repository:
    ```shell
    git clone --recurse-submodules https://github.com/rlaphoenix/slipstream
    cd slipstream
    ```
2. Install the Project with uv:
    ```shell
    uv sync --all-extras --all-groups
    ```
    This creates a Virtual environment at `.venv` and then installs all project dependencies and executables into the
    Virtual environment. Your System Python environment is not affected at all.
3. Now activate the Virtual environment:
    ```shell
    .venv\Scripts\activate
    ```
    (or `source .venv/bin/activate` on macOS and Linux)

    Note:
    - You can alternatively just prefix `uv run` to any command you wish to run under the Virtual environment.
    - I recommend entering the Virtual environment and all further instructions will have assumed you did.
    - JetBrains PyCharm and Visual Studio Code both detect the `.venv` Virtual environment automatically.
    - For more information, see: https://docs.astral.sh/uv/concepts/projects/
4. Install Pre-commit tooling to ensure safe and quality commits:
    ```shell
    uv tool install pre-commit --with pre-commit-uv --force-reinstall
    pre-commit install
    ```

Now feel free to work on the project however you like, all code will be checked before committing.

If you make any changes to the QT UI file (`main_window.ui`), then you must run `.\make.ps1` to re-compile it to its
Python file.

## Building Source and Wheel distributions

    uv build

You can optionally specify `--sdist` or `--wheel` to build that distribution only.
Built files can be found in the `/dist` directory.

## Packing with PyInstaller

    uv sync --group pack
    uv run python pyinstaller.py

You may do both `.exe` and `Folder` builds. See `--one-file` in `pyinstaller.py`.
The frozen build will be available in the `/dist` folder.

## Creating Windows Installers

1. Install the [Inno Setup Compiler](https://jrsoftware.org/isdl.php).
2. Set the `SLIPSTREAM_VERSION` environment variable, e.g. `$env:SLIPSTREAM_VERSION = uvx hatch version`.
3. Right-click the [setup.iss](setup.iss) file in the root folder and click Compile.
4. The Windows Installer will be available in the `/dist` folder.
