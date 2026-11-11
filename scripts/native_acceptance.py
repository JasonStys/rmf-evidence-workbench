"""Real frozen widget/core/history/export/unknown-state acceptance on explicit synthetic profiles. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: capture — line 102
# parameter: target — line 102
# parameter: window — line 102
# variable: load — line 108
# variable: gdi — line 109
# variable: user — line 109
# variable: pointer — line 110
# variable: arguments — line 111
# variable: library — line 111
# variable: name — line 111
# variable: result — line 111
# variable: function — line 137
# variable: handle — line 141
# variable: rectangle — line 142
# variable: height — line 145
# variable: width — line 145
# variable: source — line 148
# variable: destination — line 149
# variable: bitmap — line 150
# variable: previous — line 151
# variable: pixels — line 156
# variable: header — line 157
# variable: raw — line 175
# variable: scanlines — line 176
# variable: row — line 177
# variable: column — line 179
# variable: offset — line 180
# definition: chunk — line 183
# parameter: data — line 183
# parameter: name — line 183
# definition: oracle — line 205
# parameter: files — line 205
# parameter: index — line 205
# variable: value — line 218
# variable: expected — line 219
# variable: value — line 232
# variable: value — line 235
# variable: value — line 239
# definition: exercise — line 247
# parameter: output — line 247
# parameter: reopen — line 247
# parameter: window — line 247
# variable: deadline — line 250
# variable: receipt — line 251
# variable: expected_runs — line 265
# definition: persist — line 267
# definition: finish — line 273
# parameter: failed — line 273
# variable: name — line 280
# variable: raw — line 280
# variable: row — line 282
# definition: checked — line 287
# parameter: callback — line 287
# definition: wait — line 295
# parameter: callback — line 295
# definition: layout — line 305
# variable: original — line 307
# variable: button — line 330
# variable: name — line 330
# variable: button — line 340
# definition: rejected — line 358
# definition: export_and_reject — line 365
# variable: parent — line 369
# variable: original — line 371
# variable: target — line 374
# variable: path — line 375
# definition: completed — line 386
# parameter: index — line 386
# variable: files — line 390
# variable: desired — line 395
# variable: saved — line 431
# variable: copied — line 432
# definition: start — line 443
# parameter: index — line 443
# variable: imported — line 451
# definition: begin — line 460
# variable: identity — line 464
# END CODE MAP

from __future__ import annotations

import ctypes
import hashlib
import json
import os
import struct
import sys
import time
import zlib
from pathlib import Path
from typing import TYPE_CHECKING, Any

from rmf import desktop_project as project
from rmf.desktop_io import json_value

if TYPE_CHECKING:
    from rmf.desktop import Workbench


def capture(window: Workbench, target: Path) -> None:
    """Capture only this owned synthetic Tk window via PrintWindow, never the user's whole desktop."""
    if sys.platform != "win32":
        raise OSError("native screenshot acceptance targets Windows")
    from ctypes import wintypes

    load = ctypes.WinDLL
    user, gdi = load("user32", use_last_error=True), load("gdi32", use_last_error=True)
    pointer = ctypes.c_void_p
    for library, name, arguments, result in [
        (user, "GetAncestor", [pointer, ctypes.c_uint], pointer),
        (user, "GetWindowDC", [pointer], pointer),
        (gdi, "CreateCompatibleDC", [pointer], pointer),
        (gdi, "CreateCompatibleBitmap", [pointer, ctypes.c_int, ctypes.c_int], pointer),
        (gdi, "SelectObject", [pointer, pointer], pointer),
        (gdi, "DeleteObject", [pointer], ctypes.c_int),
        (gdi, "DeleteDC", [pointer], ctypes.c_int),
        (user, "ReleaseDC", [pointer, pointer], ctypes.c_int),
        (user, "PrintWindow", [pointer, pointer, ctypes.c_uint], ctypes.c_int),
        (user, "GetWindowRect", [pointer, ctypes.POINTER(wintypes.RECT)], ctypes.c_int),
        (
            gdi,
            "GetDIBits",
            [
                pointer,
                pointer,
                ctypes.c_uint,
                ctypes.c_uint,
                pointer,
                pointer,
                ctypes.c_uint,
            ],
            ctypes.c_int,
        ),
    ]:
        function = getattr(library, name)
        function.argtypes, function.restype = arguments, result
    # Flush this owned native window's pending control messages before reading its pixels.
    window.root.update()
    handle = user.GetAncestor(window.root.winfo_id(), 2)
    rectangle = wintypes.RECT()
    if not user.GetWindowRect(handle, ctypes.byref(rectangle)):
        raise OSError("owned window bounds unavailable")
    width, height = rectangle.right - rectangle.left, rectangle.bottom - rectangle.top
    if not 1 <= width <= 4096 or not 1 <= height <= 4096:
        raise OSError("owned screenshot outside bounded dimensions")
    source = user.GetWindowDC(handle)
    destination = gdi.CreateCompatibleDC(source)
    bitmap = gdi.CreateCompatibleBitmap(source, width, height)
    previous = gdi.SelectObject(destination, bitmap)
    try:
        if not user.PrintWindow(handle, destination, 2):
            raise OSError("owned window rendering unavailable")
        gdi.SelectObject(destination, previous)
        pixels = ctypes.create_string_buffer(width * height * 4)
        header = ctypes.create_string_buffer(
            struct.pack(
                "<IiiHHIIiiII",
                40,
                width,
                -height,
                1,
                32,
                0,
                width * height * 4,
                0,
                0,
                0,
                0,
            )
        )
        if gdi.GetDIBits(source, bitmap, 0, height, pixels, header, 0) != height:
            raise OSError("owned screenshot pixels incomplete")
        raw = pixels.raw
        scanlines = bytearray()
        for row in range(height):
            scanlines.append(0)
            for column in range(width):
                offset = (row * width + column) * 4
                scanlines.extend((raw[offset + 2], raw[offset + 1], raw[offset]))

        def chunk(name: bytes, data: bytes) -> bytes:
            """Encode a bounded standard PNG chunk with its actual CRC."""
            return (
                struct.pack(">I", len(data))
                + name
                + data
                + struct.pack(">I", zlib.crc32(name + data))
            )

        target.write_bytes(
            b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(bytes(scanlines)))
            + chunk(b"IEND", b"")
        )
    finally:
        gdi.SelectObject(destination, previous)
        gdi.DeleteObject(bitmap)
        gdi.DeleteDC(destination)
        user.ReleaseDC(handle, source)


def oracle(index: int, files: dict[str, bytes]) -> None:
    """Independent six-predicate/model/calendar and retained-tip expectations; authorization never granted."""
    if index in (0, 1):
        from rmf.oscal import FORMAT

        assert {
            "uri",
            "uri-reference",
            "iri",
            "iri-reference",
        } <= FORMAT.checkers.keys()
        assert FORMAT.conforms("https://例え.テスト/資料", "iri")
        assert not FORMAT.conforms("https://bad host/report", "iri")
        value = json_value(files["assessment.json"])
        expected = (
            {"SATISFIED": 3, "NOT_SATISFIED": 2, "UNKNOWN": 1, "INTEGRITY_ERROR": 0}
            if index == 0
            else {
                "SATISFIED": 6,
                "NOT_SATISFIED": 0,
                "UNKNOWN": 0,
                "INTEGRITY_ERROR": 0,
            }
        )
        assert value["summary"] == expected and value["authorization"] == "NOT_GRANTED"
        assert len(files) == 8 and len(value["checks"]) == 6
    elif index == 2:
        value = json_value(files["calendar.json"])
        assert len(value["events"]) == 14 and value["authorization"] == "NOT_GRANTED"
    elif index == 3:
        value = json_value(files["result.json"])
        assert len(value["changes"]) == len(value["risk_changes"]) == 3
        assert value["authorization"] == "NOT_GRANTED"
    else:
        value = json_value(files["result.json"])
        assert value["verification"]["snapshots"] == 2 and len(value["history"]) == 2
        assert value["verification"]["assurance"] == (
            "UNANCHORED_LOCAL_CHAIN" if index == 4 else "EXTERNAL_TIP_MATCH"
        )
        assert value["authorization"] == "NOT_GRANTED"


def exercise(window: Workbench, output: Path, reopen: bool) -> None:
    """Drive the same real widgets/mainloop/core with marked synthetic inputs; no arbitrary script, collector or API mock."""
    output.mkdir(mode=0o700)
    deadline = time.monotonic() + 55
    receipt: dict[str, Any] = {
        "schema": 1,
        "product": project.PRODUCT,
        "version": project.VERSION,
        **window.identity,
        "pid": os.getpid(),
        "parent_pid": os.getppid(),
        "synthetic": True,
        "reopen": reopen,
        "passed": False,
        "steps": [],
        "tcl_version": window.root.tk.call("info", "patchlevel"),
        "tk_version": window.root.tk.call("package", "require", "Tk"),
    }
    expected_runs = 6 if project.PRODUCT == "rmf-evidence-workbench" else 4

    def persist() -> None:
        """Write bounded aggregate identities/hashes only; no credentials or original private input paths."""
        (output / "acceptance.json").write_text(
            json.dumps(receipt, indent=2) + "\n", encoding="utf-8"
        )

    def finish(failed: bool = False) -> None:
        """Use ordinary Exit and retain exact original bundle identities for independent parent restart comparison."""
        receipt["passed"] = not failed
        window.acceptance_result = not failed
        receipt["bundles"] = {
            str(row["id"]): {
                name: hashlib.sha256(raw).hexdigest()
                for name, raw in window.state.files(row["id"]).items()
            }
            for row in window.state.history()
        }
        persist()
        window.exit()

    def checked(callback: Any) -> None:
        """A failed real oracle remains a failed receipt; no fallback, retry or reset is attempted."""
        try:
            callback()
        except Exception:
            receipt["failure_stage"] = callback.__name__
            finish(True)

    def wait(callback: Any) -> None:
        """Keep the real event loop responsive while this owned worker completes within its unchanged deadline."""
        if time.monotonic() > deadline:
            receipt["failure_stage"] = "owned-operation-deadline"
            finish(True)
        elif window.busy:
            window.root.after(60, lambda: wait(callback))
        else:
            checked(callback)

    def layout() -> None:
        """Real minimum-width layout keeps every lifecycle control fully visible even with long status text."""
        original = window.status.get()
        window.root.geometry("980x700")
        window.status.set(
            original
            + " Synthetic long-message layout check: existing evidence remains available and Exit waits for the owned operation."
        )
        window.root.update()
        receipt["layout"] = {
            "root": [window.root.winfo_width(), window.root.winfo_height()],
            "status": [
                window.status_label.winfo_width(),
                window.status_label.winfo_height(),
                window.status_label.winfo_reqheight(),
                int(window.status_label.cget("wraplength")),
            ],
            "buttons": {
                name: [
                    button.winfo_width(),
                    button.winfo_reqwidth(),
                    button.winfo_rootx() - window.root.winfo_rootx(),
                    button.winfo_rooty() - window.root.winfo_rooty(),
                    button.winfo_height(),
                ]
                for name, button in window.footer_buttons.items()
            },
        }
        assert (
            int(window.status_label.cget("wraplength"))
            <= window.status_label.winfo_width()
        )
        assert (
            window.status_label.winfo_height() >= window.status_label.winfo_reqheight()
        )
        for button in window.footer_buttons.values():
            assert button.winfo_width() >= button.winfo_reqwidth()
            assert button.winfo_rootx() >= window.root.winfo_rootx()
            assert (
                button.winfo_rootx() + button.winfo_width()
                <= window.root.winfo_rootx() + window.root.winfo_width()
            )
            assert (
                button.winfo_rooty() + button.winfo_height()
                <= window.root.winfo_rooty() + window.root.winfo_height()
            )
        window.status.set(original)
        window.root.geometry("1260x860")
        window.root.update()
        receipt["steps"].append(
            "real-minimum-width-long-status-all-lifecycle-controls-visible"
        )

    def rejected() -> None:
        """A mistaken user input must retain every previous bundle and report rejection instead of a new success."""
        assert len(window.state.history()) == expected_runs
        assert "rejected" in window.status.get().lower()
        receipt["steps"].append("actual-invalid-input-retains-original-history")
        finish()

    def export_and_reject() -> None:
        """The actual Export control writes exact selected evidence; the next bad input cannot replace it."""
        from unittest.mock import patch

        parent = output / "private-export"
        parent.mkdir()
        original = window.state.files(window.selected_run)
        with patch("rmf.desktop.filedialog.askdirectory", return_value=str(parent)):
            window.export_button.invoke()
        target = next(parent.iterdir())
        assert {path.name: path.read_bytes() for path in target.iterdir()} == original
        receipt["steps"].append("actual-widget-exact-export")
        if project.PRODUCT == "rmf-evidence-workbench":
            window.values["tip"].set("0" * 64)
        else:
            window.mode.set(project.MODES[2])
            window.values["horizon"].set("169")
        window.authorized.set(True)
        window.run_button.invoke()
        wait(rejected)

    def completed(index: int) -> None:
        """Check actual persisted core results, choose literal findings/details and capture only owned synthetic pixels."""
        assert len(window.state.history()) == index + 1
        assert window.selected_run == index + 1
        files = window.state.files(index + 1)
        oracle(index, files)
        if index == 0:
            layout()
        if index in (0, 2):
            desired = (
                (
                    "Original evidence predicates"
                    if index == 0
                    else "Owner work calendar"
                )
                if project.PRODUCT == "rmf-evidence-workbench"
                else (
                    "Original identity findings"
                    if index == 0
                    else "Representative nested paths"
                )
            )
            window.view.set(desired)
            window.search.set("")
            window.render()
            assert window.table.get_children()
            window.table.selection_set("0")
            window.inspect()
            window.root.update()
            assert window.view.get() == desired and isinstance(
                json.loads(window.details.get("1.0", "end")), dict
            )
            capture(
                window,
                output
                / (
                    "selected-evidence.png"
                    if index == 0
                    else "owner-unknown-review.png"
                ),
            )
        receipt["steps"].append("actual-core-scenario-" + str(index + 1))
        if index + 1 == expected_runs:
            export_and_reject()
        elif project.PRODUCT == "rmf-evidence-workbench" and index == 4:
            saved = json_value(files["result.json"])
            copied = output / "closed-synthetic-ledger.sqlite"
            copied.write_bytes(files["ledger.sqlite"])
            window.mode.set(project.MODES[4])
            window.values["ledger"].set(str(copied))
            window.values["tip"].set(saved["receipt"]["tip"])
            window.authorized.set(True)
            window.run_button.invoke()
            wait(lambda: completed(index + 1))
        else:
            start(index + 1)

    def start(index: int) -> None:
        """Prepared scenarios populate ordinary visible controls; explicit permission and actual Run remain mandatory."""
        window.prepared.set(project.SCENARIOS[index])
        window.load_prepared()
        assert not window.authorized.get()
        if index == 0:
            import shutil

            imported = output / "selected-external-workspace"
            shutil.copytree(project.ROOT / "examples/baseline", imported)
            window.values["workspace"].set(str(imported))
            assert not window.authorized.get()
            receipt["steps"].append("actual-user-selected-external-workspace")
        window.authorized.set(True)
        window.run_button.invoke()
        wait(lambda: completed(index))

    def begin() -> None:
        """First launch starts empty; second process reopens the same real saved bundles without recalculation."""
        if reopen:
            assert len(window.state.history()) == expected_runs
            for identity in range(1, expected_runs + 1):
                window.history_table.selection_set(str(identity))
                window.open_button.invoke()
                assert window.selected_run == identity
                oracle(identity - 1, window.state.files(identity))
            receipt["steps"].append("actual-process-reopen-all-exact-bundles")
            finish()
        else:
            assert window.state.history() == []
            window.run_button.invoke()
            assert not window.busy and window.state.history() == []
            start(0)

    persist()
    checked(begin)
