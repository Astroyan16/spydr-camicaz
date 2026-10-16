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
- Live chopping enable, disable and re-enable take effect on the next cycle
  without restarting acquisition or duplicating callbacks. Repeated enable
  preserves the phase; disabled chopping leaves the last mechanical position.
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

## Quadrant reconstruction

Run `python3 tools/tests/check_quadrant_mapping.py` on Linux/WSL with g++.
The real Camicaz::getLastImage function is compiled as C++98 with a synthetic
input buffer. Distinct values encode every amplifier, pixel and read. Checks
cover all 131072 output pixels of a 256x256x2 exposure, a single read, an 8x8x2
case, quadrant seams, sample uniqueness and destination memory guards.

The old half-width-minus-one origin fails this test: one quadrant is shifted,
128 pixels per read are never assigned, and a boundary is overwritten. The
fix uses half-width, preserving amplifier order and read separation without
changing sign, gain or bias. This is not a test of NI transfer or physical
detector orientation. On the instrument, inspect quadrant boundaries and compare
Start, End and Diff statistics using the rebuilt isolated library.

## Recorded chopping sequences

Run `python3 tools/tests/check_chopping_sequences.py` on Linux/WSL with Yorick.
Production pattern, recording, append, abort and save functions are extracted
verbatim. Camera, scheduler, delay, GTK and FITS writer are test doubles.

Checks cover all six menu modes, one/three cycles, both initial DTR states,
unchopped recordings, 200 ABBA cycles (800 saved exposures), 200 cycles of
ABBABAABBAABABBA (3200 saved exposures), early abort and
invalid modes/counts. They verify per-exposure DTR states, transition commands,
totals/progress, one queued callback at most, and saved frame order/count with
the initial primer frame removed. This does not test FITS serialization or the
actual mechanical synchronization.

Failure checks also cover primer/read/chopping failures, disconnect after a
read (the invalid frame must not be appended), no valid exposures, partial save,
disk errors on partial and complete cubes, Stop retry, and refusal of a new
Record while a cube is unsaved. UI commands must not unlock Record during saving.
Missing/failed Apply and all changed camera parameters are rejected before
acquisition. The freerun suite separately verifies the unsaved-cube interlock.

`python3 tools/tests/check_record_save.py` uses real Yorick FITS IO in a temporary
directory: same-name collisions, existing-file preservation, refusal to overwrite,
frame order after serialization, and an invalid-path failure followed by retry.
`python3 tools/tests/check_camera_filename.py` checks seconds and all 84 naming
combinations; optional `--bundle dist/<bundle>` checks the current delivery too.
Historical bundles are deliberately not required to match updated naming code.

`python3 tools/tests/check_camera_errors.py` needs g++ on Linux/WSL. It compiles
the production wrapper and setter functions as C++98 against hardware/API doubles.
It verifies acquisition errors (including a mid-cube failure), parameter-command
failures at each stage, and DTR failures. It is not a full NI driver/library build.

On the target, rebuild both libraries in the isolated bundle. Exercise Apply,
Stop, disconnect, and recording twice with identical parameters. Check partial
files and recovery after a destination-permission or disk-space error. Keep one
application instance per output directory: the legacy FITS writer's existence
check is not an atomic cross-process reservation.

Logical A is DTR off (0), B is DTR on (1), matching historical ABAB. Patterns
are AB, ABBA, AABB, AAAAABBBBB, ten A followed by ten B, and ABBABAABBAABABBA,
repeated per cycle. The last pattern has 16 exposures: eight A and eight B.
The menu is sampled at Record, not during a recording or freerun. Freerun still
alternates simply. Physical A/B assignment must be checked on the instrument.

On the target, validate each mode from both starting positions with short
recordings, checking exposure totals, DTR/mechanical timing and saved frames.
Confirm that the existing settling delay is sufficient before scientific use.

## Recording folder

`python3 tools/tests/check_record_folder.py` executes the production Record
callback with GTK doubles and temporary directories. It checks that the selected
folder, not the displayed parent, is transmitted on the first and subsequent
recordings, including paths with spaces. Missing, nonexistent or non-directory
selections must report an error before stopping freerun or disabling controls.
This does not exercise the native GTK dialog or FITS writing.

On the target, select a child folder without opening it, record a short sequence,
and verify that the FITS file is inside that folder, not its parent. Repeat after
browsing into the folder and after changing the selection.

## Live chopping checkbox

`python3 tools/tests/check_live_chopping.py` executes the production Python
callback with GTK doubles. Only a running freerun receives the update; the
selected sequence survives disable/re-enable (ABAB is initialized only for an
empty selection). The Yorick test above checks
the resulting alternating commands with a simulated chopping function.

On the instrument, enable and disable chopping during freerun, then repeat and
restart with each checkbox state. Verify the physical alternation and unchanged
recording behavior. Disabling stops alternation; it does not home the mechanism.

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
