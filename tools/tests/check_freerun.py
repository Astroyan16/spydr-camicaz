"""Run real Yorick/Gist regressions with a simulated camera on Linux/Xvfb.

Usage: python3 tools/tests/check_freerun.py --yorick /path/to/yorick
Requires Xvfb on PATH. Does not load NI drivers or launch the camera UI.
"""

import argparse
import ctypes as C
import hashlib
import os
from pathlib import Path
import re
import selectors
import shutil
import subprocess
import tempfile
import time


def extract(text, kind, name):
    # Mask comments and strings to count only language-level braces.
    masked = re.sub(r'/\*.*?\*/|//[^\n]*|"(?:\\.|[^"\\])*"',
                    lambda m: " " * len(m[0]), text, flags=re.S)
    start = re.search(r"\b" + kind + r"\s+" + name + r"\b", masked).start()
    brace = masked.index("{", start)
    depth = 1
    end = brace + 1
    while depth:
        depth += (masked[end] == "{") - (masked[end] == "}")
        end += 1
    return text[start:end] + (";" if kind == "struct" else "") + "\n"


class XImage(C.Structure):
    _fields_ = [("width", C.c_int), ("height", C.c_int),
                ("xoffset", C.c_int), ("format", C.c_int),
                ("data", C.c_void_p), ("byte_order", C.c_int),
                ("bitmap_unit", C.c_int), ("bitmap_bit_order", C.c_int),
                ("bitmap_pad", C.c_int), ("depth", C.c_int),
                ("bytes_per_line", C.c_int), ("bits_per_pixel", C.c_int)]


class Screen:
    def __init__(self, display):
        self.x = C.CDLL("libX11.so.6")
        self.x.XOpenDisplay.argtypes = [C.c_char_p]
        self.x.XOpenDisplay.restype = C.c_void_p
        self.x.XDefaultRootWindow.argtypes = [C.c_void_p]
        self.x.XDefaultRootWindow.restype = C.c_ulong
        self.x.XGetImage.argtypes = [C.c_void_p, C.c_ulong, C.c_int, C.c_int,
                                    C.c_uint, C.c_uint, C.c_ulong, C.c_int]
        self.x.XGetImage.restype = C.POINTER(XImage)
        self.x.XDestroyImage.argtypes = [C.POINTER(XImage)]
        self.x.XCloseDisplay.argtypes = [C.c_void_p]
        self.display = self.x.XOpenDisplay(display.encode())
        if not self.display:
            raise RuntimeError("Cannot connect to test X server")
        self.root = self.x.XDefaultRootWindow(self.display)

    def digest(self):
        img = self.x.XGetImage(self.display, self.root, 0, 0, 800, 600,
                              C.c_ulong(-1).value, 2)
        if not img:
            raise RuntimeError("Cannot read test framebuffer")
        try:
            return hashlib.sha256(C.string_at(
                img.contents.data, img.contents.bytes_per_line * 600)).hexdigest()
        finally:
            self.x.XDestroyImage(img)

    def close(self):
        self.x.XCloseDisplay(self.display)


def rss(pid):
    status = Path(f"/proc/{pid}/status").read_text()
    return int(re.search(r"VmRSS:\s+(\d+)", status)[1])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--yorick", default=shutil.which("yorick"))
    args = parser.parse_args()
    if not args.yorick or not shutil.which("Xvfb"):
        parser.error("yorick and Xvfb are required")
    repo = Path(__file__).resolve().parents[2]
    source = repo / "PC TP IR/TP_Master_version/yCamicaz/yorick/spydr"
    main_src = (source / "spydr.i").read_text()
    camera_src = (source / "spydr_widgetcam.i").read_text()
    code = extract(main_src, "struct", "spydr_struct")
    for name in ("disp_tv", "spydr_draw_tv_frame", "spydr_resize_main", "spydr", "spydr_clean", "set_imnum"):
        code += extract(main_src, "func", name)
    for name in ("cam_stop_freerun", "cam_start_freerun", "freerun_loop",
                 "cam_disp_select", "cam_load"):
        code += extract(camera_src, "func", name)
    code += Path(__file__).with_name("freerun_checks.i").read_text()

    with tempfile.TemporaryDirectory(prefix="spydr-render-") as tmp:
        script = Path(tmp) / "check.i"
        script.write_text(code)
        ack = Path(tmp) / "ack"
        os.mkfifo(ack)
        rfd, wfd = os.pipe()
        server = subprocess.Popen(["Xvfb", "-displayfd", str(wfd), "-screen",
                                   "0", "800x600x24", "-nolisten", "tcp",
                                   "-nolisten", "unix"],
                                  pass_fds=(wfd,))
        os.close(wfd)
        proc = screen = None
        try:
            with os.fdopen(rfd) as ready:
                display = ":" + ready.readline().strip()
            screen = Screen(display)
            proc = subprocess.Popen([args.yorick, "-batch", str(script)],
                                    stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT, text=True, bufsize=1,
                                    env={**os.environ, "DISPLAY": display,
                                         "SPYDR_TEST_ACK": str(ack),
                                         "GISTPATH": str(source) + ":" + os.environ.get(
                                             "GISTPATH", "/usr/share/yorick/gist")})
            samples = []
            probes = {}
            passed = False
            # A dedicated FIFO avoids Yorick's interactive stdin handling.
            # Read one byte at a time
            # so select() is not defeated by buffered read-ahead.
            selector = selectors.DefaultSelector()
            selector.register(proc.stdout, selectors.EVENT_READ)
            line = bytearray()
            deadline = time.monotonic() + 180
            while time.monotonic() < deadline:
                if not selector.select(1):
                    continue
                byte = os.read(proc.stdout.fileno(), 1)
                if not byte:
                    break
                line.extend(byte)
                if byte != b"\n":
                    continue
                message = line.decode(errors="replace").strip()
                line.clear()
                print(message, flush=True)
                if message.startswith("PROBE_"):
                    probes[message] = screen.digest()
                    with ack.open("w") as stream:
                        stream.write("continue\n")
                if message.startswith("MEMORY "):
                    samples.append((rss(proc.pid), rss(server.pid)))
                    print(f"RSS KiB (Yorick, Xvfb): {samples[-1]}", flush=True)
                    with ack.open("w") as stream:
                        stream.write("continue\n")
                passed |= message.startswith("PASS freerun:")
            else:
                raise RuntimeError("Yorick test timed out")
            if proc.wait(timeout=5) or not passed or len(samples) != 6:
                raise AssertionError("Yorick regression failed")
            assert probes["PROBE_BASE"] == probes["PROBE_PENDING"], "partial frame visible"
            assert probes["PROBE_BASE"] != probes["PROBE_DONE"], "new frame not presented"
            assert probes["PROBE_DONE"] == probes["PROBE_REDRAW"], "last frame lost on redraw"
            # Allow allocator caches, but not an image retained on each frame.
            for idx in (0, 1):
                growth = max(s[idx] for s in samples[1:]) - samples[0][idx]
                assert growth < 16 * 1024, f"unbounded RSS growth: {growth} KiB"
            print("PASS visible frame atomicity, redraw and bounded RSS (3000 frames)")
        finally:
            if proc and proc.poll() is None:
                proc.kill(); proc.wait()
            if screen:
                screen.close()
            server.terminate(); server.wait(timeout=5)


if __name__ == "__main__":
    main()
