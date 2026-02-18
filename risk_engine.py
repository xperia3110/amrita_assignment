def calculate_risk(data):
    """
    Calculates patient risk based on deterministic rules.
    
    Input:
        data (dict): Dictionary containing patient parameters.
        Keys expected: 
        - age (int)
        - heart_rate (int)
        - systolic_bp (int)
        - spo2 (int)
        - temperature (float)
        - respiratory_rate (int)
        - history (list of strings, e.g., ['Diabetes'])
        - er_visits (int) - Last 30 days
        - lab_issues (list of strings, e.g., ['Elevated WBC'])

    Output:
        dict: {
            'score': int,
            'label': str (LOW, MEDIUM, HIGH),
            'notes': list (Explanation of score)
        }
    """
    score = 0
    notes = []
    critical_triggers = []

    age = data.get('age', 0)
    hr = data.get('heart_rate', 0)
    bp = data.get('systolic_bp', 0)
    spo2 = data.get('spo2', 100)
    temp = data.get('temperature', 37.0)
    resp = data.get('respiratory_rate', 18)
    history = data.get('history', [])
    er_visits = data.get('er_visits', 0)
    lab_issues = data.get('lab_issues', [])

    # CRITICAL ESCALATION PROTOCOL

    if spo2 < 85:
        critical_triggers.append(f"Critical: SpO2 {spo2}% (<85%)")
    
    if bp < 80:
        critical_triggers.append(f"Critical: Systolic BP {bp} (<80 mmHg)")
        
    if hr > 140:
        critical_triggers.append(f"Critical: Heart Rate {hr} (>140 bpm)")

    # STANDARD SCORING ENGINE

    if 60 <= age <= 75:
        score += 1
        notes.append("Age 60-75")
    elif age > 75:
        score += 2
        notes.append("Age >75")

  
    if 100 <= hr <= 120:
        score += 1
        notes.append("HR 100-120")
    elif hr > 120:
        score += 2
        notes.append("HR >120")


    if bp < 90:
        score += 2
        notes.append("Systolic BP <90")


    if 90 <= spo2 <= 93:
        score += 1
        notes.append("SpO2 90-93%")
    elif spo2 < 90:
        score += 2
        notes.append("SpO2 <90%")


    if 38 <= temp <= 39:
        score += 1
        notes.append("Temp 38-39°C")
    elif temp > 39:
        score += 2
        notes.append("Temp >39°C")

    if resp > 24:
        score += 1
        notes.append("Resp Rate >24")

    # Clinical History
    valid_conditions = [
        "Diabetes", "COPD", "Cardiac Disease", "Cardiac",
        "Hypertension", "High Blood Pressure",
        "Stroke", "CVA",
        "Kidney Disease", "Renal Failure",
        "Cancer", "Malignancy",
        "Asthma",
        "Heart Failure", "CHF",
        "Pneumonia"
    ]
    condition_count = 0
    unrecognized_conditions = []

    for cond in history:
        if not cond or not cond.strip():
            continue
        matched = False
        for valid in valid_conditions:
            if valid.lower() in cond.lower():
                condition_count += 1
                score += 1
                notes.append(f"History: {cond}")
                matched = True
                break
        
        if not matched:
            unrecognized_conditions.append(cond)
            notes.append(f"WARNING: Unrecognized condition '{cond}'")

    if 2 <= er_visits <= 3:
        score += 1
        notes.append("ER Visits 2-3")
    elif er_visits > 3:
        score += 2
        notes.append("ER Visits >3")

    # Lab Indicators
    valid_labs = ["Elevated WBC", "High Creatinine", "High CRP"]
    
    for lab in lab_issues:
        if not lab or not lab.strip():
            continue
            
        matched = False
        for valid in valid_labs:
            if valid.lower() in lab.lower():
                score += 1
                notes.append(f"Lab: {lab}")
                matched = True
                break
        
        if not matched:
            notes.append(f"WARNING: Unrecognized lab '{lab}'")

    # FINAL CLASSIFICATION
  
    label = "LOW"
    
    if critical_triggers:
        label = "HIGH"
        notes.insert(0, " CRITICAL ESCALATION TRIGGERED ")
        notes.extend(critical_triggers)
    else:
        if score >= 6:
            label = "HIGH"
        elif score >= 3:
            label = "MEDIUM"
        else:
            label = "LOW"

    return {
        "score": score,
        "label": label,
        "notes": notes,
        "unrecognized_conditions": unrecognized_conditions
    }