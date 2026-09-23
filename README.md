# Diagnostic Report PDF to Structured JSON Converter

A Python-based tool that extracts content from diagnostic lab report PDFs and converts them into structured JSON format.

## Project Overview

In diagnostics, many lab reports are available as PDF files. This tool extracts the contents and converts them into structured JSON, useful for report migration, patient history, analytics, and clinical intelligence features.

## Features

- Upload a text-based diagnostic report PDF
- Extract raw text from the PDF using pdfplumber
- Parse patient details (name, age, gender, ID, contact, referring doctor)
- Parse test parameters (name, value, unit, reference range, abnormal flag) from tabular reports
- Handle descriptive reports (Histopathology, Ultrasound, Echo, X-ray) with section-wise parsing
- Display structured JSON output on screen
- Download JSON file

## Supported Report Types

### Tabular Reports
- CBC (Complete Blood Count)
- LFT (Liver Function Test)
- LPT (Lipid Profile Test)
- RFT (Renal Function Test)

### Descriptive Reports
- Histopathology / Biopsy
- Ultrasound
- Echocardiography
- X-Ray

## Technology Stack

- Python 3.12
- pdfplumber (PDF text extraction)
- Regex / rule-based parsing
- Streamlit (frontend)

## How to Run

1. Clone the repository
2. Create a virtual environment and activate it
3. Install dependencies
4. Run the Streamlit app

```bash
git clone https://github.com/vaishnavidbhandary1806-bit/-diagnostic-report-parser.git
cd -diagnostic-report-parser
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Scope

- Text-based PDFs only
- Scanned PDFs and OCRy are future enhancements
