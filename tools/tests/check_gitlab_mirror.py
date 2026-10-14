"""Check workflow shell syntax and branch/tag synchronization without credentials."""
from pathlib import Path
import os
import subprocess
import tempfile
import yaml

ROOT = Path(__file__).resolve().parents[2]
workflow = yaml.safe_load((ROOT / ".github/workflows/sync-gitlab.yml").read_text())
script = workflow["jobs"]["sync"]["steps"][0]["run"]
shell = ["wsl", "-d", "Ubuntu", "--", "bash"] if os.name == "nt" else ["bash"]
subprocess.run(shell + ["-n"], input=script.encode(), check=True)


def git(*args):
    return subprocess.check_output(["git", *map(str, args)], stderr=subprocess.STDOUT,
                                   text=True).strip()


with tempfile.TemporaryDirectory(prefix="spydr-mirror-") as folder:
    root = Path(folder)
    source, mirror, destination = (root / name for name in ("source", "mirror", "dest"))
    git("init", "-b", "main", source)
    git("-C", source, "config", "user.name", "Mirror test")
    git("-C", source, "config", "user.email", "mirror@example.invalid")
    git("-C", source, "commit", "--allow-empty", "-m", "Initial")
    git("-C", source, "branch", "feature")
    git("-C", source, "tag", "v0.9.0-test")
    git("clone", "--bare", source, mirror)
    git("init", "--bare", destination)
    refs = ["+refs/heads/*:refs/heads/*", "+refs/tags/*:refs/tags/*"]
    git("-C", mirror, "push", "--atomic", "--prune", destination, *refs)
    assert git("-C", destination, "rev-parse", "main") == git("-C", source, "rev-parse", "main")
    # Exercise both a new commit and deleted branch/tag propagation.
    git("-C", source, "commit", "--allow-empty", "-m", "Update")
    git("-C", source, "branch", "-D", "feature")
    git("-C", source, "tag", "-d", "v0.9.0-test")
    refreshed = root / "refreshed"
    git("clone", "--bare", source, refreshed)
    git("-C", refreshed, "push", "--atomic", "--prune", destination, *refs)
    assert git("-C", destination, "show-ref") == git("-C", source, "show-ref")

print("Workflow shell syntax and local branch/tag mirror verified.")
