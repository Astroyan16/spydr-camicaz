"""Read production Yorick FITS output with independent Astropy validation.

On Windows this runs Yorick through WSL; no camera or GTK is required.
"""
from pathlib import Path
import base64
import json
import os
import subprocess
import tempfile
import argparse

import numpy as np
from astropy.io import fits

from check_freerun import extract

SOURCE = Path(__file__).resolve().parents[2] / "PC TP IR/TP_Master_version/yCamicaz/yorick/spydr"


def linux_path(path):
    if os.name != "nt":
        return str(path)
    return subprocess.check_output(
        ["wsl", "-d", "Ubuntu", "--", "wslpath", "-a", path.as_posix()], text=True).strip()


original = dict(object="Saturne / anneaux", observer="Zo\u00e9 O'Neil",
                comments=('Mesure \u00e0 77 K, "fond" et \\test\n' * 60),
                focal_length_mm=10000., software_version="metadata-test")
payload = base64.b64encode(json.dumps(original).encode("utf-8")).decode("ascii")
source = (SOURCE / "spydr_widgetcam.i").read_text()
code = (SOURCE / "spydr_metadata.i").read_text() + "\n"
parser = argparse.ArgumentParser()
parser.add_argument("--fits-library", type=Path, help="Optional historical fits.i to exercise")
args = parser.parse_args()
if args.fits_library:
    code = code.replace('require,"fits.i";',
                        'require,' + json.dumps(linux_path(args.fits_library.resolve())) + ';', 1)
for name in ("cam_unique_filename", "camdata_save"):
    code += extract(source, "func", name)

with tempfile.TemporaryDirectory(prefix="spydr-metadata-") as folder:
    folder = Path(folder)
    (folder / "camicaz.ini").write_text("[NI]\n\nportList = Dev1/port2,Dev1/port3\n")
    if os.name == "nt":
        support = Path(__file__).with_name("native_clock_test_support.py")
        subprocess.run(["wsl", "-d", "Ubuntu", "--", "python3", linux_path(support),
                        linux_path(folder)], check=True)
        prefix = 'plug_dir,_(' + json.dumps(linux_path(folder)) + ',plug_dir());\nplug_in,"testclock";\n'
    else:
        from native_clock_test_support import build_clock_plugin
        prefix = build_clock_plugin(folder)
    full, missing, partial = [folder / (name + ".fits") for name in ("full", "missing", "partial")]
    code += '''
cam_config="camicaz.ini";
cam_last_probes=[50,45,65,60]; cam_last_probe_time=1700000000.;
cam_metadata_begin,1,"Saturne / anneaux",1,1,2,3,2,"Zoe O'Neil","ASCII summary",
'''
    code += json.dumps(payload) + ',10000.,"metadata-test";\n'
    code += '''
cam_meta(8)=1700000010.; cam_meta_end=1700000020.;
cam_meta_reason="Recording complete.";
cam_seqpattern=[0,1,1,0]; cam_nimseq=4; cam_seqind=4;
cam_frame_log=array(0.,12,4);
cam_frame_log(1,)=[60000.,60001.,60002.,60003.];
cam_frame_log(2,)=cam_frame_log(1,)+1./86400.;
cam_frame_log(3,)=[0,1,1,0];
cam_frame_log(4,)=1700000010.; cam_frame_log(5,)=123456789.;
cam_frame_log(6,)=1700000010.; cam_frame_log(7,)=123656790.;
cam_frame_log(8,)=1000.; cam_frame_log(9,)=123456789.;
cam_frame_log(10,)=1000.; cam_frame_log(11,)=123656790.;
cam_frame_log(12,)=0.000200001;
cam_buffer=array(999,2,2,2,5);
for (i=1;i<=4;i++) cam_buffer(,,,i+1)=i;
// Mutating current settings must not alter the record snapshot.
spydr_pixsize=99.; cam_last_probes=[1,1,1,1];
'''
    code += 'cam_filename=' + json.dumps(linux_path(full)[:-5]) + ';\ncamdata_save,0;\n'
    code += '''
cam_last_probes=[]; cam_last_probe_time=[];
cam_metadata_begin,2,"test",2,-1,0,0,0,"","","",0.,"metadata-test";
cam_seqpattern=[]; cam_frame_log=[]; cam_seqind=1; cam_nimseq=1;
cam_buffer=array(999,2,2,2,2); cam_buffer(,,,2)=42;
cam_meta_end=cam_meta(8); cam_meta_reason="Recording complete.";
'''
    code += 'cam_filename=' + json.dumps(linux_path(missing)[:-5]) + ';\ncamdata_save,0;\n'
    code += '''
cam_seqind=1; cam_nimseq=4; cam_meta_reason="Recording stopped; acquired exposures saved.";
cam_buffer=array(999,2,2,2,2); cam_buffer(,,,2)=43;
'''
    code += 'cam_filename=' + json.dumps(linux_path(partial)[:-5]) + ';\ncamdata_save,0;\nquit;\n'
    script = folder / "check.i"
    with script.open("w", newline="\n") as stream:
        stream.write(prefix + 'camtop=' + json.dumps(linux_path(folder)) + ';\n' + code)
    command = ["yorick", "-batch", linux_path(script)]
    if os.name == "nt":
        command = ["wsl", "-d", "Ubuntu", "--"] + command
    result = subprocess.run(command, capture_output=True, text=True, timeout=45)
    assert result.returncode == 0, result.stdout + result.stderr

    with fits.open(full) as hdus:
        hdus.verify("exception")
        header = hdus[0].header
        assert hdus[0].data.shape == (4, 2, 2, 2)
        for i in range(4):
            assert np.all(hdus[0].data[i] == i + 1)
        assert header["OBSERVER"] == "Zoe O'Neil"
        assert header["FILTER"] == "H" and header["EXPTIME"] == 0.110
        assert header["LATENCY"] == 0.130 and header["OBSTYPE"] == "Science"
        assert header["CHOPPAT"] == "ABBA" and header["NREQUEST"] == 4
        assert header["NSAVED"] == 4 and not header["PARTIAL"]
        assert header["READ1"] == "Start" and header["READ2"] == "End"
        assert not header["BGSUB"] and header["FOCVALID"]
        assert abs(header["PIXSCALE"] - 0.8250592249883855) < 1e-12
        assert header["FOCALLEN"] == 10000.
        assert header["HKRAW2"] == 45 and header["TEMP2"] == 67.5
        assert header["HKAGE"] == 10
        assert header["DATE-OBS"] == "2023-11-14T22:13:30.000000Z"
        assert header["DATE-END"] == "2023-11-14T22:13:40.000000Z"
        assert header["METAVER"] == 2 and header["TIMESRC"] == "clock_gettime"
        assert header["TIMEPREC"] < 1.e-3 and header["MONORES"] > 0
        encoded = "".join(header["META%04d" % i] for i in range(1, header["METACNT"] + 1))
        assert json.loads(base64.b64decode(encoded)) == original
        assert np.array_equal(hdus["FRAMELOG"].data[:, 2], [0, 1, 1, 0])
        assert np.all(hdus["FRAMELOG"].data[:, 1] >= hdus["FRAMELOG"].data[:, 0])
        assert hdus["FRAMELOG"].data.shape == (4, 12)
        assert np.all(hdus["FRAMELOG"].data[:, 4] == 123456789.)
        assert np.all(hdus["FRAMELOG"].data[:, 6] == 123656790.)
        assert np.all(hdus["FRAMELOG"].data[:, 11] == 0.000200001)
        assert "portList = Dev1/port2,Dev1/port3" in str(header["COMMENT"])
    with fits.open(missing) as hdus:
        hdus.verify("exception")
        assert hdus[0].data.shape == (2, 2, 2)
        assert np.all(hdus[0].data == 42)
        assert not hdus[0].header["HKVALID"] and not hdus[0].header["FOCVALID"]
        assert "TEMP1" not in hdus[0].header and "FOCALLEN" not in hdus[0].header
    with fits.open(partial) as hdus:
        assert hdus[0].header["PARTIAL"]
        assert hdus[0].header["NSAVED"] == 1 and hdus[0].header["NREQUEST"] == 4
        assert np.all(hdus[0].data == 43)
print("PASS FITS metadata: independent Astropy verification, Unicode/long text, snapshot, frame log, missing and partial acquisitions")
