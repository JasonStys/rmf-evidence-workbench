"""Build the complete real offline workbench as one Windows portable executable. Jason Stys.

No publication, installation, shortcut change, host collection or Docker action.
"""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ROOT — line 89
# definition: runtime_names — line 93
# variable: names — line 95
# definition: icon — line 106
# parameter: path — line 106
# variable: size — line 108
# variable: pixels — line 109
# variable: y — line 110
# variable: x — line 111
# variable: shield — line 112
# variable: check — line 118
# variable: color — line 124
# variable: bitmap — line 132
# definition: notices — line 146
# parameter: path — line 146
# variable: root — line 150
# variable: tcl_version — line 153
# variable: tk_version — line 154
# variable: value — line 157
# variable: runtime_notices — line 162
# variable: library — line 163
# variable: title — line 163
# variable: channel — line 167
# variable: raw — line 169
# variable: raw — line 173
# variable: sources — line 181
# variable: name — line 185
# variable: suffix — line 185
# variable: distribution — line 186
# variable: matches — line 187
# variable: entry — line 188
# variable: item — line 200
# variable: blocks — line 202
# variable: source — line 203
# variable: title — line 203
# variable: name — line 205
# variable: distribution — line 206
# variable: entries — line 207
# variable: entry — line 209
# variable: entry — line 215
# variable: notice — line 216
# variable: stream — line 217
# variable: content — line 218
# variable: _ — line 226
# variable: data — line 226
# variable: data — line 229
# variable: title — line 229
# definition: main — line 233
# variable: version — line 242
# variable: source — line 245
# variable: dirty — line 248
# variable: output — line 253
# variable: release — line 253
# variable: resource_paths — line 258
# variable: name — line 268
# variable: metadata — line 270
# variable: name — line 278
# variable: path — line 278
# variable: command — line 284
# variable: name — line 305
# variable: path — line 305
# variable: command — line 308
# variable: name — line 309
# variable: command — line 310
# variable: name — line 312
# variable: command — line 313
# variable: command — line 314
# variable: executable — line 328
# variable: stream — line 329
# variable: digest — line 330
# END CODE MAP

import hashlib
import importlib.metadata
import json
import os
import re
import struct
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def runtime_names() -> tuple[str, ...]:
    """Inventory the exact locked runtime graph, excluding validation-only tools and the replaced GPL format leaf."""
    names = tuple(
        re.findall(
            r"(?m)^([a-z0-9_.-]+)(?:\[[^\]]+\])?==",
            (ROOT / "requirements.lock").read_text(encoding="utf-8"),
        )
    )
    if not names or len(names) != len(set(names)) or "rfc3987" in names:
        raise ValueError("Review the exact native runtime dependency inventory")
    return names


def icon(path: Path) -> None:
    """Generate an authored blue shield/check icon as build output, without shipping a graphics dependency."""
    size = 64
    pixels = bytearray()
    for y in reversed(range(size)):
        for x in range(size):
            shield = (
                8 <= x <= 55
                and 5 <= y <= 42
                or 42 < y <= 59
                and abs(x - 31.5) < (60 - y) * 1.4
            )
            check = (
                15 <= x <= 29
                and abs(y - (x + 8)) < 3
                or 27 <= x <= 48
                and abs(y - (65 - x)) < 3
            )
            color = (
                (255, 255, 255, 255)
                if shield and check
                else (220, 100, 24, 255)
                if shield
                else (0, 0, 0, 0)
            )
            pixels.extend(color)
    bitmap = (
        struct.pack(
            "<IIIHHIIIIII", 40, size, size * 2, 1, 32, 0, len(pixels), 0, 0, 0, 0
        )
        + pixels
        + bytes(size * size // 8)
    )
    path.write_bytes(
        struct.pack("<HHH", 0, 1, 1)
        + struct.pack("<BBBBHHII", size, size, 0, 0, 1, 32, len(bitmap), 22)
        + bitmap
    )


def notices(path: Path) -> None:
    """Retain actual Python, Tcl/Tk, application-runtime and bootloader notices, including Tcl9 DLL-embedded resources."""
    import tkinter

    root = tkinter.Tk()
    root.withdraw()
    try:
        tcl_version = root.tk.call("info", "patchlevel")
        tk_version = root.tk.call("package", "require", "Tk")
        if not all(
            str(value).startswith(("8.6.", "9.0."))
            for value in (tcl_version, tk_version)
        ):
            raise ValueError(
                "Review a different Tcl/Tk runtime family before packaging"
            )
        runtime_notices = []
        for title, library in [
            ("Tcl " + str(tcl_version), root.tk.call("info", "library")),
            ("Tk " + str(tk_version), root.tk.eval("set tk_library")),
        ]:
            channel = root.tk.call("open", str(library) + "/license.terms", "rb")
            try:
                raw = root.tk.call("read", channel, 65537)
            finally:
                root.tk.call("close", channel)
            if isinstance(raw, str):
                raw = raw.encode("utf-8")
            if not isinstance(raw, bytes) or not 100 < len(raw) <= 65536:
                raise ValueError(
                    "Actual runtime notice is missing or outside its byte bound"
                )
            runtime_notices.append((title, raw))
    finally:
        root.destroy()
    sources = [
        ("Authored application — MIT", ROOT / "LICENSE"),
        ("Python runtime", Path(sys.base_prefix) / "LICENSE.txt"),
    ]
    for name, suffix in [("pyinstaller", "licenses/COPYING.txt")]:
        distribution = importlib.metadata.distribution(name)
        matches = [
            entry for entry in distribution.files or [] if str(entry).endswith(suffix)
        ]
        if len(matches) != 1:
            raise ValueError("Review runtime license inventory before packaging")
        sources.append(
            (
                name + " license and applicable exception",
                Path(distribution.locate_file(matches[0])),
            )
        )
    sources.extend(
        ("Unmodified NIST OSCAL schema notice", ROOT / item)
        for item in ("schemas/NIST-NOTICE.md", "schemas/NOTICE.md")
    )
    blocks = [
        (title, source.read_bytes()) for title, source in sources
    ] + runtime_notices
    for name in runtime_names():
        distribution = importlib.metadata.distribution(name)
        entries = [
            entry
            for entry in distribution.files or []
            if entry.name.casefold().startswith(("license", "copying", "notice"))
            or ".dist-info/licenses/" in str(entry)
        ]
        if not entries or len(entries) > 20:
            raise ValueError("Runtime license inventory needs explicit review")
        for entry in entries:
            notice = Path(distribution.locate_file(entry))
            with notice.open("rb") as stream:
                content = stream.read(2 * 1024 * 1024 + 1)
            if not content or len(content) > 2 * 1024 * 1024:
                raise ValueError(
                    "Actual dependency notice is missing or exceeds its bound"
                )
            blocks.append(
                (name + " " + distribution.version + " — " + entry.name, content)
            )
    if any(len(data) > 2 * 1024 * 1024 for _, data in blocks):
        raise ValueError("Bundled license exceeds byte bound")
    path.write_bytes(
        b"\n\n".join(title.encode("utf-8") + b"\n" + data for title, data in blocks)
    )


def main() -> None:
    """Freeze exact allowlisted public resources and bind actual source/dirty state without publishing."""
    if sys.platform != "win32" or sys.version_info[:3] != (3, 14, 10):
        raise RuntimeError(
            "This portable recipe requires patched Windows CPython3.14.10"
        )
    from rmf import desktop_project as project
    from rmf.desktop_io import read_bytes

    version = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]["version"]
    if version != project.VERSION:
        raise ValueError("Native version coherence failed")
    source = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()
    dirty = bool(
        subprocess.check_output(
            ["git", "status", "--porcelain"], cwd=ROOT, text=True
        ).strip()
    )
    release, output = ROOT / "release", ROOT / "out"
    release.mkdir(exist_ok=True)
    output.mkdir(exist_ok=True)
    notices(release / "notices.txt")
    icon(output / "app.ico")
    resource_paths = {
        name: (
            release / name
            if name == "notices.txt"
            else output / name
            if name == "app.ico"
            else Path(sys.base_prefix) / name
            if name == "python314.dll"
            else ROOT / name
        )
        for name in project.RESOURCES
    }
    metadata = {
        "schema": 1,
        "product": project.PRODUCT,
        "version": version,
        "source": source,
        "source_dirty": dirty,
        "resources": {
            name: hashlib.sha256(read_bytes(path, 32 * 1024 * 1024)).hexdigest()
            for name, path in resource_paths.items()
        },
    }
    (release / "native-release.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf8"
    )
    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onefile",
        "--windowed",
        "--icon",
        str(output / "app.ico"),
        "--name",
        "RmfEvidenceWorkbench",
        "--distpath",
        "release/portable",
        "--workpath",
        "out/native-build",
        "--specpath",
        "out",
        "--paths",
        str(ROOT),
    ]
    for name, path in resource_paths.items():
        if name == "python314.dll":
            continue  # PyInstaller collects the actual interpreter DLL as a binary, not duplicate data.
        command += ["--add-data", str(path) + os.pathsep + Path(name).parent.as_posix()]
    for name in runtime_names():
        command += ["--copy-metadata", name]
    # Include only immutable installed-wheel grammar/schema data, never selected user files.
    for name in ("rfc3987_syntax", "lark", "jsonschema_specifications"):
        command += ["--collect-data", name]
    command += [
        "--add-data",
        str(release / "native-release.json") + os.pathsep + ".",
        "scripts/native_entry.py",
    ]
    subprocess.run(
        command,
        cwd=ROOT,
        check=True,
        env={
            **os.environ,
            "PYINSTALLER_CONFIG_DIR": str(output / "native-freezer-cache"),
        },
    )
    executable = release / "portable/RmfEvidenceWorkbench.exe"
    with executable.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    executable.with_name(executable.name + ".sha256").write_text(
        digest + "  " + executable.name + "\n", encoding="ascii"
    )
    print(
        "Portable candidate built; source_dirty="
        + str(dirty)
        + "; not published or installed"
    )


if __name__ == "__main__":
    main()
