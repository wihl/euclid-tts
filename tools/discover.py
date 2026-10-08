"""Read-only capability probes; never print credentials or account details."""
import json
import platform
from pathlib import Path

import google.auth
import requests
from google.auth.transport.requests import AuthorizedSession

result = {"architecture": platform.machine()}
try:
    credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    response = AuthorizedSession(credentials).get(
        "https://texttospeech.googleapis.com/v1/voices", params={"languageCode": "el-GR"}, timeout=30
    )
    result["google_status"] = response.status_code
    if response.ok:
        result["google_voices"] = response.json().get("voices", [])
    else:
        error = response.json().get("error", {})
        result["google_error"] = {"status": error.get("status"), "reasons": [d.get("reason") for d in error.get("details", []) if "reason" in d]}
except Exception as exc:
    result["google_exception"] = type(exc).__name__

for repo in ["onnx-community/Kokoro-82M-v1.0-ONNX", "rhasspy/piper-voices"]:
    try:
        response = requests.get(f"https://huggingface.co/api/models/{repo}", timeout=30)
        response.raise_for_status()
        data = response.json()
        result[repo] = {"revision": data["sha"], "files": [f["rfilename"] for f in data["siblings"] if f["rfilename"] in ["config.json", "voices/af_heart.bin", "voices/af_bella.bin", "onnx/model_quantized.onnx"] or "el_GR/rapunzel" in f["rfilename"]]}
    except Exception as exc:
        result[repo] = {"exception": type(exc).__name__}
Path("work").mkdir(exist_ok=True)
Path("work/discovery.json").write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n")
print(json.dumps(result, ensure_ascii=False, indent=2))
