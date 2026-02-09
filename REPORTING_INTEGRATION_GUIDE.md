<<<<<<< Updated upstream
<<<<<<< Updated upstream
# S1P Report Integration Guide

## Overview

Your ATR (Antenna Testing and Reporting) system now has fully integrated S1P file analysis and PDF report generation capabilities. This document explains how to use the new reporting features.

## What's New

=======
## Overview

>>>>>>> Stashed changes
=======
## Overview

>>>>>>> Stashed changes
### New Modules

1. **`reporting/` folder** - Main reporting system
   - `ReportManager.py` - Core S1P processing engine
   - `antennareport_lib/` - Supporting libraries for analysis, plotting, and report generation

2. **GUI Integration** - New "Reports" tab in the ATR Control Window
   - Visual interface for report generation
   - Batch processing of S1P files
   - Single file processing with metadata

## Installation

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

Key new dependencies:
- `scikit-rf` - For S-parameter network analysis
- `reportlab` - For PDF generation

### Step 2: Verify Structure

The following structure should exist:
```
Final-2025-Release/
├── reporting/
│   ├── __init__.py
│   ├── ReportManager.py
│   └── antennareport_lib/
│       ├── __init__.py
│       ├── analysis.py
│       ├── io.py
│       ├── plots.py
│       └── report.py
├── gui/
│   ├── ReportGeneratorView.py
│   ├── ReportGeneratorViewController.py
│   └── GUIManager.py (modified)
└── requirements.txt
```

## Usage

### Via GUI (Recommended)

1. **Launch ATR**: `python ATR.py`
2. **Click "Reports" tab** in the control window
3. **Configure options**:
   - **Data Directory**: Where your `.s1p` files are located
   - **Reports Directory**: Where generated reports will be saved
   - **Design Freq (GHz)**: Optional design frequency for analysis (e.g., `2.4`)
   - **Author**: Your name for report attribution
   - **Notes**: Additional metadata for the report

4. **Process Files**:
   - **Process All S1P Files**: Generates reports for all `.s1p` files in the data directory
   - **Process Single File**: Select a specific `.s1p` file to process

### Via Python Script

```python
from reporting import ReportManager

# Create manager
report_mgr = ReportManager(
    data_dir="./data",
    reports_dir="./reports"
)

# Process single file
result = report_mgr.process_single_s1p(
    s1p_file="./data/antenna_test.s1p",
    design_freq_ghz=2.4,
    notes="Test antenna at 2.4 GHz",
    author="Your Name"
)

# Or process all files
results = report_mgr.process_all_s1p_files(
    directory="./data",
    author="Your Name"
)
```

## File Format Requirements

### S1P Files
- Standard Touchstone S-parameter files (single port)
- Frequency in Hz, magnitude in dB
- Example: `antenna_test.s1p`

### Metadata Files (Optional)
- Plain text files with name: `antenna_test.meta.txt`
- Key-value format, one per line
- Supported keys:
  ```
  design_freq_ghz: 2.4
  notes: Additional antenna notes here
  ```

### Example Metadata File
```
design_freq_ghz: 2.4
notes: Spherical measurement, 1-6 GHz, 361x91 points
```

## Output Files

For each `.s1p` file processed, three files are generated:

1. **`{antname}_S11.png`** - S11 magnitude plot with peak markers
2. **`{antname}_Smith.png`** - Smith chart with impedance loci
3. **`{antname}.pdf`** - Comprehensive PDF report containing:
   - Title page with design frequency
   - Table of S11 minima (first 4 peaks)
   - All available plots and measurement data
   - Author and timestamp information

## Output Report Contents

### Page 1: Title Page
- Antenna name
- Report title and subtitle
- Generation timestamp
- Design frequency (if provided)
- Author name
- Additional notes

### Page 2: S11 Minima Table
- Peak index and frequency
- S11 magnitude in dB
- Designed frequency analysis (if applicable)

### Pages 3+: Figures
- S11 magnitude plot
- Smith chart
- Any additional antenna pattern images (3D, Phi, Theta, front, back views)

## Analysis Details

### S11 Peak Detection
- Finds first 4 S11 minima using scipy peak detection
- Configurable threshold (default: -4 dB)
- Includes peak properties (spacing, width)

### Design Frequency Analysis
- Optional analysis around specified design frequency
- Shows minimum within ±0.5 GHz window
- Reports S11 value at exact design frequency

### Smith Chart Visualization
- Reflection coefficient trajectories
- Color-coded minima markers
- Impedance visualization across frequency band

## Integration with Existing Features

### Data Management
- Reports use same data directory structure as scan data
- Metadata follows ATR naming conventions
- Compatible with existing CSV/HDF5 storage

### GUI Components
- Integrated into tabbed interface (Reports tab)
- Real-time status messages during processing
- Threading prevents GUI freezing during batch operations
- Error handling and user feedback

### Extensibility
- Modular `antennareport_lib` can be extended
- Easy to add new plot types
- Report template customizable via `report.py`

## Troubleshooting

### "Module not found" errors
```bash
pip install scikit-rf reportlab
```

### S1P files not found
- Verify directory path is correct
- Check files have `.s1p` extension (case-sensitive on Linux)
- Files should be in the specified data directory

### PDF generation fails
- Ensure `reportlab` is installed
- Check that output directory is writable
- Verify image files are valid PNG/JPG

### Missing images in PDF
- Place pattern images in data directory
- Use naming convention: `{antname}_3D.png`, `{antname}_front.png`, etc.
- Supported suffixes: `_3D`, `_phi`, `_theta`, `_front`, `_back`, `_S11`, `_Smith`

## Example Workflow

```python
# 1. Create data directory and add files
# ./data/
#   ├── patch_antenna_2GHz.s1p
#   ├── patch_antenna_2GHz.meta.txt
#   ├── horn_antenna_5GHz.s1p
#   └── horn_antenna_5GHz.meta.txt

# 2. Run from GUI or script
from reporting import ReportManager

mgr = ReportManager("./data", "./reports")

# Process all S1P files
results = mgr.process_all_s1p_files(
    author="Jane Rodriguez",
    clean_reports_first=True
)

# 3. Output generated to ./reports/
# ./reports/
#   ├── patch_antenna_2GHz_S11.png
#   ├── patch_antenna_2GHz_Smith.png
#   ├── patch_antenna_2GHz.pdf
#   ├── horn_antenna_5GHz_S11.png
#   ├── horn_antenna_5GHz_Smith.png
#   └── horn_antenna_5GHz.pdf
```

## Performance Notes

- Processing speed depends on S1P file size and frequency resolution
- Typical small files (< 10k points): < 1 second per file
- Large files (> 100k points): 2-5 seconds per file
- Batch processing is optimized for multi-file workflows

## Support

For issues or questions:
1. Check the status messages in the Reports tab
2. Review error logs in the terminal window
3. Verify file formats match Touchstone S1P standard
4. Ensure all dependencies are up-to-date

## Future Enhancements

Potential additions:
- Multi-port S2P/S3P/S4P support
- Additional plot types (group delay, phase)
- Batch report compilation into single PDF
- S-parameter mathematical operations
- Antenna efficiency calculations
- Gain pattern integration

---

**Integration Date**: February 2026  
**Version**: 1.0  
**Based on**: antennareport project by Jaden Gangwer
