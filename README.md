# Patient Risk Monitor

![Status](https://img.shields.io/badge/Status-Active-success)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Flask](https://img.shields.io/badge/Backend-Flask-lightgrey)
![License](https://img.shields.io/badge/License-MIT-green)

A comprehensive **Patient Risk Monitoring System** designed to streamline clinical data collection, automate risk assessment using a deterministic rule-based engine, and maintain a rigorous audit trail for compliance and patient safety.

---

## Features

### 1. Smart Data Collection
*   **Manual Entry:** Intuitive forms for detailed demographics, vitals, clinical history, and lab indicators.
*   **Document Parsing:** Upload PDF medical reports to **auto-fill** admission forms using advanced rule-based extraction (`pdfplumber`).

### 2. Risk Calculation Engine
*   **Deterministic Scoring:** Strictly follows clinical rules for Age, Vitals, History, and Labs.
*   **Critical Escalation:** Automatically flags **"HIGH"** risk for critical values:
    *   SpO2 < 85%
    *   Systolic BP < 80 mmHg
    *   Heart Rate > 140 bpm
*   **Real-time Recalculation:** Risk scores and labels update instantly whenever patient data is modified.

### 3. Modern User Interface
*   **Dashboard:** Real-time analytics with Risk Distribution (Donut Chart) and 7-day Admission Trends (Line Chart).
*   **Patient List:** Sortable list with color-coded risk status indicators for quick triage.
*   **Patient Details:** Unified view to monitor patient status, edit parameters, and review risk factors.

### 4. Comprehensive Audit System
*   **Timeline:** Chronological tracking of every modification to patient records.
*   **Diff View:** detailed "Old Value" vs "New Value" comparison for all changes.
*   **Risk Trace:** Explicitly records how risk levels evolve with each clinical update.

---


## Project Structure

```
├── app.py              # Main Flask Application
├── risk_engine.py      # Deterministic Risk Scoring Logic
├── service_pdf.py      # PDF Parsing Service
├── models.py           # Database Models (Patient, AuditLog)
├── requirements.txt    # Python Dependencies
├── templates/          # HTML Templates
│   ├── base.html
│   ├── dashboard.html
│   ├── patient_list.html
│   ├── patient_details.html
│   └── add_patient.html
├── instance/           # Database Storage (risk_system.db)
└── tests/              # Unit Tests
```

## Setup Instructions

### Prerequisites
*   Python 3.8+
*   pip

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/xperia3110/amrita_assignment.git
    cd amrita_assignment
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### Database Configuration
The application uses **SQLite**. The database file `risk_system.db` will be automatically created in the `instance` folder upon the first run.

---

## Running the Application

1.  **Start the Flask server:**
    ```bash
    python3 app.py
    ```

2.  **Access the Dashboard:**
    Open your browser and navigate to:
    [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## Testing

To run the comprehensive test suite (Risk Engine, PDF Parsing, Web Routes):

```bash
python3 tests/test_suite.py
```

The test suite automatically configures the environment (in-memory DB) and avoids polluting your real database.

---

## Limitations
*   **Mobile App:** This project is implemented as a Responsive Web Application only.

---

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
