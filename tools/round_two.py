"""Run the five bounded follow-up candidates and their short controls."""
import shutil

import yaml

from euclid_tts.__main__ import VOICE_NAMES, build, qc, validate
from euclid_tts.text import ROOT
from final_report import main as report


def main():
    configs = sorted((ROOT/"experiments").glob("round-2-*.yaml"))
    for control in [True, False]:
        for full_config in configs:
            path = full_config.parent/"short"/full_config.name if control else full_config
            cfg = validate(yaml.safe_load(path.read_text()))
            build(cfg, (path.parent/cfg["output"]["directory"]).resolve())
    for candidate, name in [("erasmian-google", "erasmian"), ("modern-wavenet", "modern_female")]:
        stem = VOICE_NAMES[name]
        for suffix in [".wav", ".mp3", ".json"]:
            shutil.copy2(ROOT/"output/round-2"/candidate/(stem+suffix), ROOT/"output"/(stem+suffix))
    qc(ROOT/"output")
    report()


if __name__ == "__main__":
    main()
