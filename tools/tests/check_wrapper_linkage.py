"""Check codger-style builtin linkage with g++ (Linux/WSL, no NI hardware)."""

from pathlib import Path
import subprocess
import tempfile


repo = Path(__file__).resolve().parents[2]
headers = repo / "PC TP IR/yorick.git/relocate/include"
with tempfile.TemporaryDirectory(prefix="spydr-linkage-") as directory:
    source = Path(directory) / "wrapper.c"
    obj = Path(directory) / "wrapper.o"
    source.write_text(
        '#include "play.h"\n#include "ydata.h"\n'
        'extern BuiltIn Y_yCamicaz_is_open;\n'
        'BuiltIn *camera_status = &Y_yCamicaz_is_open;\n'
    )
    for language in ("c++", "c"):
        subprocess.run(
            ["g++", "-x", language, "-fPIC", "-I", str(headers),
             "-c", str(source), "-o", str(obj)], check=True
        )
        symbols = subprocess.check_output(["nm", "-u", str(obj)], text=True)
        expected = ("_Z18Y_yCamicaz_is_openi" if language == "c++"
                    else "Y_yCamicaz_is_open")
        assert expected in symbols.split(), symbols
        if language == "c":
            assert "_Z18Y_yCamicaz_is_openi" not in symbols, symbols
        print(f"PASS {language}: {expected}")
