import re
import json

def parse_patient_details(text):
    patient = {}

    name_match = re.search(r'Patient Name\s*:\s*(.+?)\s+Reg/Lab No', text)
    if name_match:
        patient['name'] = name_match.group(1).strip()

    reg_match = re.search(r'Reg/Lab No\.\s*:\s*([\w/\s]+?)(?:\n|Age/Sex)', text)
    if reg_match:
        patient['reg_no'] = reg_match.group(1).strip()

    age_match = re.search(r'Age/Sex\s*:\s*(\d+\s*\w+)\s*/\s*(\w+)', text)
    if age_match:
        patient['age'] = age_match.group(1).strip()
        patient['gender'] = age_match.group(2).strip()

    contact_match = re.search(r'Contact No\.\s*:\s*(\d+)', text)
    if contact_match:
        patient['contact'] = contact_match.group(1).strip()

    date_match = re.search(r'Date of Report\s*:\s*([\d\-]+\s*at\s*[\d:]+\s*[APM]+)', text)
    if date_match:
        patient['date_of_report'] = date_match.group(1).strip()

    ref_match = re.search(r'Ref\. By\.\s*:\s*(.+)', text)
    if ref_match:
        patient['referred_by'] = ref_match.group(1).strip()

    return patient


def parse_test_results(text):
    results = []

    row_pattern = re.compile(
        r'^([A-Za-z][A-Za-z0-9\.\(\)\-\s/]*?)\s*'
        r'([\d\.]+)\s*'
        r'(?:\(\s*([LH])\s*\))?\s*'
        r'([A-Za-z/%]+)?\s+'
        r'((?:up to\s*[\d\.]+)|(?:[\d\.]+\s*-\s*[\d\.]+)|(?:[\d\.]+\s*:\s*\d+\s*to\s*\d+\s*:\s*\d+))'
    )

    for line in text.split('\n'):
        line = line.strip()
        if not line:
            continue

        match = row_pattern.match(line)
        if match:
            param, value, flag, unit, ref_range = match.groups()
            results.append({
                "parameter": param.strip(),
                "value": value.strip(),
                "flag": flag if flag else "Normal",
                "unit": unit.strip() if unit else None,
                "reference_range": ref_range.strip()
            })

    return results


def build_json(text, report_type="UNKNOWN"):
    patient = parse_patient_details(text)
    tests = parse_test_results(text)

    structured = {
        "patient_details": {
            "name": patient.get("name"),
            "age": patient.get("age"),
            "gender": patient.get("gender"),
            "reg_no": patient.get("reg_no"),
            "contact": patient.get("contact"),
            "referred_by": patient.get("referred_by")
        },
        "report_metadata": {
            "report_type": report_type,
            "date_of_report": patient.get("date_of_report")
        },
        "test_results": tests
    }

    return structured


def parse_descriptive_report(text):
    findings = {}

    fields = {
        "method": r'METHOD\s*:\s*(.+?)(?=BIOPSY NO|NATURE OF|CLINICAL|GROSS|MICROSCOPY|IMPRESSION|$)',
        "biopsy_no": r'BIOPSY NO\s*:\s*(.+?)(?=NATURE OF|CLINICAL|GROSS|MICROSCOPY|IMPRESSION|$)',
        "specimen": r'NATURE OF SPECIMEN\s*:\s*(.+?)(?=CLINICAL|GROSS|MICROSCOPY|IMPRESSION|$)',
        "clinical_diagnosis": r'CLINICAL DIAGNOSIS\s*:\s*(.+?)(?=GROSS|MICROSCOPY|IMPRESSION|$)',
        "gross": r'GROSS\s*:\s*(.+?)(?=MICROSCOPY|IMPRESSION|$)',
        "microscopy": r'MICROSCOPY\s*:\s*(.+?)(?=IMPRESSION|$)',
        "impression": r'IMPRESSION\s*:\s*(.+?)(?=NOTE|Page \d|Dispatched|$)',
    }

    for key, pattern in fields.items():
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            findings[key] = ' '.join(match.group(1).strip().split())

    return findings


def parse_echo_report(text):
    findings = {}

    fields = {
        "measurements": r'Measurements\s*:\s*(.+?)(?=VALVES|CHAMBERS|SEPTAE|$)',
        "valves": r'VALVES\s*(.+?)(?=CHAMBERS|SEPTAE|$)',
        "chambers": r'CHAMBERS\s*(.+?)(?=SEPTAE|GREAT ARTERIES|$)',
        "septae": r'SEPTAE\s*(.+?)(?=GREAT ARTERIES|DOPPLER|$)',
        "great_arteries": r'GREAT ARTERIES\s*(.+?)(?=DOPPLER|WALL MOTION|$)',
        "doppler": r'DOPPLER DATA & COLOUR FLOW\s*(.+?)(?=WALL MOTION|OTHER FINDINGS|$)',
        "wall_motion": r'WALL MOTION ABNORMALITIES\s*:\s*(.+?)(?=Pericardium|OTHER FINDINGS|$)',
        "other_findings": r'OTHER FINDINGS\s*:\s*(.+?)(?=FINAL DIAGNOSIS|$)',
        "final_diagnosis": r'FINAL DIAGNOSIS\s*:\s*(.+?)(?=Page \d|Dispatched|Dr |$)',
    }

    for key, pattern in fields.items():
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            findings[key] = ' '.join(match.group(1).strip().split())

    return findings


def parse_xray_report(text):
    findings = {}

    title_match = re.search(r'(XRAY.+?)(?=Observations)', text, re.DOTALL | re.IGNORECASE)
    if title_match:
        findings['exam_type'] = ' '.join(title_match.group(1).strip().split())

    fields = {
        "observations": r'Observations\s*(.+?)(?=Impression|$)',
        "impression": r'Impression\s*(.+?)(?=Page \d|Dispatched|$)',
    }

    for key, pattern in fields.items():
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            findings[key] = ' '.join(match.group(1).strip().split())

    return findings


def parse_ultrasound_report(text):
    findings = {}

    title_match = re.search(r'(ULTRASOUND.+?)(?=\n\s*-)', text, re.DOTALL | re.IGNORECASE)
    if title_match:
        findings['exam_type'] = ' '.join(title_match.group(1).strip().split())

    fields = {
        "observations": r'(?:' + (title_match.group(1) if title_match else 'ULTRASOUND') + r')\s*(.+?)(?=IMPRESSION)',
        "impression": r'IMPRESSION\s*:?\s*(.+?)(?=Page \d|Dispatched|$)',
    }

    for key, pattern in fields.items():
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            findings[key] = ' '.join(match.group(1).strip().split())

    return findings


def build_descriptive_json(text, report_type="HISTOPATHOLOGY"):
    patient = parse_patient_details(text)

    if report_type.upper() == "ECHO":
        findings = parse_echo_report(text)
    elif report_type.upper() == "XRAY":
        findings = parse_xray_report(text)
    elif report_type.upper() == "ULTRASOUND":
        findings = parse_ultrasound_report(text)
    else:
        findings = parse_descriptive_report(text)

    structured = {
        "patient_details": {
            "name": patient.get("name"),
            "age": patient.get("age"),
            "gender": patient.get("gender"),
            "reg_no": patient.get("reg_no"),
            "contact": patient.get("contact"),
            "referred_by": patient.get("referred_by")
        },
        "report_metadata": {
            "report_type": report_type,
            "date_of_report": patient.get("date_of_report")
        },
        "findings": findings,
        "test_results": []
    }

    return structured


if __name__ == "__main__":
    import pdfplumber
    import sys

    pdf_path = sys.argv[1]
    report_type = sys.argv[2] if len(sys.argv) > 2 else "UNKNOWN"

    descriptive_types = ["HISTOPATHOLOGY", "XRAY", "ULTRASOUND", "ECHO"]

    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() or ""

    if report_type.upper() in descriptive_types:
        output = build_descriptive_json(text, report_type)
    else:
        output = build_json(text, report_type)

    print(json.dumps(output, indent=4))

    output_file = pdf_path.replace(".pdf", ".json")
    with open(output_file, "w") as f:
        json.dump(output, f, indent=4)

    print(f"\nJSON saved to: {output_file}")