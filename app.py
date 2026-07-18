import streamlit as st
import pdfplumber
import json
from parse import build_json, build_descriptive_json

DESCRIPTIVE_TYPES = ["HISTOPATHOLOGY", "XRAY", "ULTRASOUND", "ECHO"]

st.title("Diagnostic Report PDF → JSON Converter")

uploaded_file = st.file_uploader("Upload a diagnostic PDF report", type=["pdf"])

report_type = st.selectbox("Select Report Type", [
    "CBC", "LFT", "LPT", "RFT",
    "HISTOPATHOLOGY", "ULTRASOUND", "XRAY", "ECHO"
])

if uploaded_file is not None:
    with st.spinner("Extracting text from PDF..."):
        with pdfplumber.open(uploaded_file) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""

    if report_type.upper() in DESCRIPTIVE_TYPES:
        output = build_descriptive_json(text, report_type)
    else:
        output = build_json(text, report_type)

    st.subheader("Structured JSON Output")
    st.json(output)

    json_str = json.dumps(output, indent=4)
    st.download_button(
        label="Download JSON",
        data=json_str,
        file_name=f"{report_type}.json",
        mime="application/json"
    )