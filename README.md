# RotoPDF

**English** | [Français](README.fr.md)

Turns a video into numbered image sheets in a PDF.

- Choose how many frames per second (fps) to extract
- Choose how many images per page (automatic layout, portrait or landscape)
- Each image is numbered, with the video time shown as an option
- Simple dark interface, Windows installer provided

## Install

Download `RotoPDF_Setup.exe` from the **Releases** section and run it.

### Windows warning at install time

Releases are not digitally signed yet, so Windows SmartScreen may show
"Windows protected your PC". Click **More info**, then **Run anyway**.
The SHA-256 checksum of each installer is published with the release
(`RotoPDF_Setup.exe.sha256`) so you can verify your download.

## Run from source

```
pip install -r requirements.txt
python rotopdf.py
```

Or double-click `lancer.bat` (Windows).

## Build the installer (Windows)

1. Install Python 3.10 or newer and [Inno Setup](https://jrsoftware.org/isdl.php) (free, version 6 or 7).
2. Double-click `creer_installateur.bat`.
3. The installer is created in `Output\RotoPDF_Setup.exe`.

`creer_exe.bat` builds a single portable exe instead (`dist\RotoPDF.exe`).
Releases are also built automatically by GitHub Actions (`.github/workflows/build.yml`).

## Code Signing Policy

An application to the free code signing program of the SignPath Foundation is planned.
If it is accepted, Windows releases will be built automatically by GitHub Actions from this
public repository and then signed: "Free code signing provided by SignPath.io, certificate by
SignPath Foundation".

- **Author, reviewer and approver:** Mattt6
- **Privacy:** this program works offline and does not transfer any information to other
  networked systems.

## License

Copyright (C) 2026 Mattt6

Released under the GNU GPL v3 or later, see [LICENSE](LICENSE).
Third-party components are listed in [THIRD_PARTY_NOTICES.txt](THIRD_PARTY_NOTICES.txt).
