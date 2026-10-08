import json
from pathlib import Path
import requests

for repo in ["hexgrad/Kokoro-82M", "onnx-community/Kokoro-82M-v1.0-ONNX"]:
    response = requests.get(f"https://huggingface.co/api/models/{repo}", timeout=30)
    response.raise_for_status()
    data = response.json()
    print(repo, data["sha"])
    files = [f["rfilename"] for f in data["siblings"]]
    print([p for p in files if p.endswith(".json")])
    for name in ["config.json", "tokenizer.json", "tokenizer_config.json"]:
        if name in files:
            result = requests.get(f"https://huggingface.co/{repo}/resolve/{data['sha']}/{name}", timeout=30)
            result.raise_for_status()
            Path(f"work/{repo.split('/')[0]}-{name}").write_text(result.text)
            print(name, list(result.json())[:20])
