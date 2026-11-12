# DXF Room Function Numbering Tool

Streamlit app for numbering identical room-function TEXT/MTEXT labels while leaving other drawing entities intentionally untouched.

## Deploy to Streamlit Community Cloud
1. Create a GitHub repository.
2. Upload `app.py`, `requirements.txt`, and the `.streamlit` folder.
3. In Streamlit Community Cloud choose **Create app** / **Deploy an app**.
4. Select the repository and branch, and set the main file path to `app.py`.
5. Deploy.

## Memory design
- Recommended DXF upload: <= 40 MB.
- Streamlit upload hard limit configured at 50 MB.
- DXF is parsed once per rerun and is not cached.
- Uploaded raw bytes are deleted after parsing.
- No CAD canvas/PNG preview is generated.
- Output is serialized once for download.

## Current scope
- TEXT and MTEXT.
- Scans modelspace and layouts.
- Exact cleaned-room-label matching.
- Independent numbering for each room function.
- Block ATTRIB room names are not included yet.

Always test on a copy of a production DXF first.
