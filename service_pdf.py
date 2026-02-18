import pdfplumber
import re

def extract_data_from_pdf(filepath):
    """
    Extracts patient data from a PDF medical report using rule-based regex parsing.
    
    Args:
        filepath (str): Path to the PDF file.
        
    Returns:
        dict: Extracted data compatible with the add_patient form.
    """
    text = ""
    try:
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return {}

    data = {}
    
    # Helper for regex extraction
    def extract(pattern, type_func=str):
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                val = match.group(1).strip()
                return type_func(val)
            except:
                return None
        return None

    # Extraction Rules
    data['name'] = extract(r"(?:Patient )?Name[:\s]+([a-zA-Z ]+)(?:[\(\n,]|$)")
    data['age'] = extract(r"(?:Age[:\s]+|\(Age[:\s]+)(\d+)", int)
    
    # Gender
    data['gender'] = extract(r"Gender[:\s]+(Male|Female|Other)")
    
    # HR: Heart Rate or HR
    data['heart_rate'] = extract(r"(?:Heart Rate|HR)[:\s]+(\d+)", int)
    
    # BP: Systolic BP or BP xxx/yyy
    bp_match = re.search(r"(?:BP|Blood Pressure)[:\s]+(\d+)/(\d+)", text, re.IGNORECASE)
    if bp_match:
        data['systolic_bp'] = int(bp_match.group(1))
        data['diastolic_bp'] = int(bp_match.group(2))
    else:
        data['systolic_bp'] = extract(r"(?:Systolic BP|SBP)[:\s]+(\d+)", int)
        data['diastolic_bp'] = extract(r"(?:Diastolic BP|DBP)[:\s]+(\d+)", int)
    
    # SpO2
    data['spo2'] = extract(r"(?:SpO2|Saturation)[:\s]+(\d+)", int)
    
    # Temperature: Temp or Temperature, handle "C" 
    data['temperature'] = extract(r"(?:Temperature|Temp)[:\s]+([\d\.]+)", float)
    
    # Respiratory Rate: Respiratory Rate or Resp
    data['respiratory_rate'] = extract(r"(?:Respiratory Rate|Resp)[:\s]+(\d+)", int)
    
    # History
    # Capture text after "History:" until next keyword or end of sentence/line
    history_match = re.search(r"(?:Medical History|Clinical History|History)[:\s]+(.*?)(?:\n\.|Wait for it|$)", text, re.IGNORECASE | re.DOTALL)
    if history_match:
        raw_hist = history_match.group(1).split('.')[0]
        data['history'] = [h.strip() for h in raw_hist.split(',') if h.strip()]
        
    # Lab
    lab_match = re.search(r"(?:Lab Results|Lab Indicators|Labs)[:\s]+(.*?)(?:\n\.|Wait for it|$)", text, re.IGNORECASE | re.DOTALL)
    if lab_match:
        raw_lab = lab_match.group(1).split('.')[0]
        data['lab_issues'] = [l.strip() for l in raw_lab.split(',') if l.strip()]

    return data
