"""Run the five bounded follow-up candidates and their short controls."""
import yaml

from euclid_tts.__main__ import build, validate
from euclid_tts.text import ROOT
from final_report import main as report


def main():
    configs = sorted((ROOT/"experiments").glob("round-2-*.yaml"))
    for control in [True, False]:
        for full_config in configs:
            path = full_config.parent/"short"/full_config.name if control else full_config
            cfg = validate(yaml.safe_load(path.read_text()))
            build(cfg, (path.parent/cfg["output"]["directory"]).resolve())
    # Historical two-sentence trials must not replace the current defaults.
    cfg = validate(yaml.safe_load((ROOT/"config.yaml").read_text()))
    build(cfg, (ROOT/cfg["output"]["directory"]).resolve())
    report()


if __name__ == "__main__":
    main()
