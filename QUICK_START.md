# Quick Start: S1P Report Generation

## 5-Minute Setup

### 1. Install Dependencies
```bash
cd e:\VSCODESTUFF\Final-2025-Release
pip install -r requirements.txt
```

### 2. Prepare Your Data
Create a `data` folder with your `.s1p` files:
```
data/
├── antenna1.s1p
├── antenna1.meta.txt    (optional)
├── antenna2.s1p
└── antenna2.meta.txt    (optional)
```

### 3. Run ATR
```bash
python ATR.py
```

### 4. Generate Reports
- Click the **Reports** tab
- Click **Process All S1P Files** or select a single file
- Reports appear in the `reports/` folder

## Meta File Format (Optional)

Create `antenna1.meta.txt`:
```
design_freq_ghz: 2.4
notes: My antenna notes here
```

## Output

Each processed file generates:
- `antenna1_S11.png` - Frequency response plot
- `antenna1_Smith.png` - Smith chart
- `antenna1.pdf` - Complete report

## Programmatic Usage

```python
from reporting import ReportManager

mgr = ReportManager("./data", "./reports")
results = mgr.process_all_s1p_files(author="Your Name")
```

---

For full documentation, see: `REPORTING_INTEGRATION_GUIDE.md`
