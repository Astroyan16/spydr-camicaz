# Freerun rendering regression

Release version checks (Python 3, no camera or GTK required):
`python3 tools/tests/check_version.py`. These check package metadata and execute
the GUI version initialization and title updates with GTK doubles.

Run on Linux (or WSL) with Python 3, Yorick, Xvfb and libX11 installed:

```sh
python3 tools/tests/check_freerun.py
```

The test extracts the actual rendering, image-stack and freerun functions from
the active source. It uses real Yorick/Gist graphics on a private Xvfb display,
but replaces camera access, GTK communication and auxiliary plots with stubs.
No camera connection or NI driver is required.

Checks include:

- Return from an 800-exposure cube (200 ABBA cycles) to a full-frame live image
  despite a simulated stale vertical crop. The cube is synthetic; acquisition,
  chopping and FITS saving are not exercised by this framing check.
- Ordinary freerun restarts preserve a deliberately selected zoom.
- The visible frame remains unchanged while its replacement is being drawn.
- A completed frame changes the display and survives an explicit redraw.
- 100 graphics-window recreations preserve the zoom limits and palette.
- Live frames replace the image stack even when ordinary append is enabled.
- Start/End/Diff selection and background subtraction still work.
- First start without a previous snapshot initializes the display selection.
- Duplicate starts, stops, acquisition/render failures and 100 restart cycles.
- 3000 frames with one displayed image, one camera cube and at most one queued
  acquisition callback in the scheduler test double.
- Yorick and Xvfb resident memory sampled every 500 frames; growth above 16 MiB
  after warm-up fails the test. Allocator caching can cause small variations.

The real timer cancellation API is also exercised. Scheduler cardinality is
asserted with a test double, not by inspecting Yorick's internal timer queue.

This is a regression test, not a proof that the entire application is leak-free.
The old bundled Yorick, GTK/PyGTK, NI driver, zoom/histogram windows, contour/3D
display and real camera must still be validated on the experimental setup.

## Resizable window

`python3 tools/tests/check_window_resize.py` exercises the real Python callbacks
with GTK and timer doubles. It checks debounce, one outstanding backend request,
latest-size delivery, startup waiting, error recovery state and timer cleanup.
It does not replace a PyGTK 2 test on the target PC.

On the target, maximize/restore and drag both window dimensions, with freerun
running and stopped. Check the startup minimum, image proportions, preserved zoom
and palette, lower/plugins panels, and repeated resizing without memory growth.
The main image fits using the smaller available dimension; unused space is normal
and avoids stretching the camera image. Rebuilding the graph occurs after a
200 ms pause in resizing, not for each mouse movement.
