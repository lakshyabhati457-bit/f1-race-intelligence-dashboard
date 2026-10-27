"""Download and unpack the public Formula 1 CSV archive."""
import io, urllib.request, zipfile, os, sys
from pathlib import Path

URL = "https://github.com/TracingInsights/RaceData/releases/latest/download/data.zip"
OUT = Path("data")
OUT.mkdir(exist_ok=True)
print("Downloading dataset archive from:", URL)
try:
    req = urllib.request.Request(URL, headers={"User-Agent":"F1-Race-Intelligence-Student-Project"})
    with urllib.request.urlopen(req, timeout=90) as response:
        payload = response.read()
    with zipfile.ZipFile(io.BytesIO(payload)) as z:
        members = [n for n in z.namelist() if n.lower().endswith(".csv")]
        wanted = {"results.csv","races.csv","drivers.csv","constructors.csv","circuits.csv","status.csv"}
        extracted = []
        for member in members:
            name = Path(member).name
            if name in wanted:
                target = OUT / name
                target.write_bytes(z.read(member))
                extracted.append(name)
    missing = wanted - set(extracted)
    print("Extracted:", ", ".join(sorted(extracted)))
    if missing:
        print("WARNING: expected files not found:", ", ".join(sorted(missing)))
        print("Inspect the release archive and adjust download_data.py if its file structure has changed.")
    else:
        print("Dataset ready. Start with: streamlit run app.py")
except Exception as exc:
    print("Download failed:", exc)
    print("Download data.zip manually from the source repository Releases page and extract the six CSVs into ./data/")
    sys.exit(1)
