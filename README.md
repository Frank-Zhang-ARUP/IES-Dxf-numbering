# DXF Room Function Numbering Tool

Streamlit app for numbering identical room-function TEXT/MTEXT labels.

## Deploy
Upload `app.py`, `requirements.txt`, and `.streamlit/config.toml` to GitHub, then deploy `app.py` on Streamlit Community Cloud.

## Memory / compatibility design
- Recommended upload <= 40 MB; server limit 50 MB.
- No Streamlit cache stores the DXF document.
- Uploaded bytes are written once to an ephemeral temp file and immediately released after parsing.
- `ezdxf.readfile()` handles the DXF header/codepage directly instead of forcing UTF-8/GB18030 decoding.
- Output is written to an ephemeral DXF file and only the final download bytes are retained.
- No drawing preview or geometry rasterization.

## Scope
- TEXT and MTEXT in modelspace/paperspace layouts.
- Numbering restarts for each selected room function.
- ATTRIB inside blocks is not yet included.
