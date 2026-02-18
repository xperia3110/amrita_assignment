# Amrita Risk Monitor

A Patient Risk Monitoring System designed to capture patient data, calculate clinical risk using a deterministic rule-based scoring engine, and maintain a complete audit history.

## Features Implemented

1.  **Patient Data Collection**
    *   **Manual Entry:** Comprehensive form for demographics, vitals, clinical history, lab indicators, and notes.
    *   **Document Parsing:** Upload PDF medical reports to auto-fill the admission form using rule-based extraction (`pdfplumber`).

2.  **Risk Calculation Engine**
    *   **Deterministic Scoring:** strictly follows the provided rules for Age, Vitals, History, and Labs.
    *   **Critical Escalation:** Automatically flags "HIGH" risk for critical values (SpO2 < 85%, SBP < 80, HR > 140).
    *   **Real-time Recalculation:** Updates risk score/label whenever patient data is modified.

3.  **User Interface**
    *   **Dashboard:** Analytics with risk distribution (Donut Chart) and admission trends (Line Chart).
    *   **Patient List:** Sortable list with quick risk status indicators.
    *   **Patient Details:** Unified view to see patient info, edit parameters, and view risk factors.

4.  **Audit System**
    *   **Timeline:** Tracks every change to patient records.
    *   **Diff View:** Shows "Old Value" vs "New Value" for all modified fields.
    *   **Risk Trace:** explicitly records how risk levels change with each update.

## Setup Instructions

### Prerequisites
*   Python 3.8+
*   pip

### Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/xperia3110/amrita_assignment.git
    cd amrita_assignment
    ```

2.  Create and activate a virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### database Configuration
The application uses SQLite. The database file `risk_system.db` will be automatically created in the `instance` folder upon the first run.

### Running the Application

1.  Start the Flask server:
    ```bash
    python3 app.py
    ```

2.  Open your browser and navigate to:
    `http://127.0.0.1:5000`
## Missing Requirements
*   **Mobile App:** This project is implemented as a Web Application only.
