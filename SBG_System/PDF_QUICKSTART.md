# PDF Report Generation - Quick Start

## What's New?

The Smart Battery Guardian now includes **PDF Report Generation**! Download comprehensive battery assessment reports directly from the dashboard.

## Quick Start (2 minutes)

### 1. Open the Dashboard
```
http://localhost:5000
```

### 2. Load Data
- Click **"📊 Load Real Data"** button
- Wait for confirmation message
- Real CALCE battery data loads

### 3. Run Analysis
- Click **"🔍 Run Analysis"** button
- Wait for analysis to complete (~10-30 seconds)
- Results display on dashboard

### 4. Download PDF Report
- Click **"📥 Download PDF Report"** button
- PDF automatically downloads to your computer
- File named: `battery_report_YYYYMMDD_HHMMSS.pdf`

## What's in the PDF?

### Executive Summary Page
- Fleet overview statistics
- Average risk scores
- Healthy vs. Warning/Critical counts
- Key findings

### Battery Assessment Pages
For each analyzed battery:
- **Overall Risk Score** (percentage)
- **Risk Level** (Healthy/Caution/Warning/Critical)
- **Thermal Analysis** (temperature, anomalies)
- **Acoustic Analysis** (fault detection metrics)
- **RUL Prediction** (remaining cycles, capacity fade)
- **Anomaly Detection** (detected issues, error metrics)
- **Maintenance Recommendation**

## Example

### Sample Report (3 batteries analyzed)

**Battery B0005** - CAUTION (42% Risk)
- Temperature: 38.5°C (normal)
- Impedance rise: 0.038Ω (elevated)
- RUL: 1,250 cycles
- Recommendation: Monitor closely, schedule maintenance within 30 days

**Battery B0006** - CRITICAL (78% Risk)
- Temperature: 52.3°C (high)
- Multiple acoustic faults detected
- RUL: 340 cycles (rapid degradation)
- Recommendation: IMMEDIATE ACTION - urgent inspection needed

**Battery B0007** - HEALTHY (18% Risk)
- All metrics normal
- RUL: 2,890 cycles
- Recommendation: No action needed, continue monitoring

## Features

✅ **Professional Formatting**
- Color-coded risk levels
- Well-organized tables
- Clear visual hierarchy

✅ **Complete Data**
- All agent analysis results
- Historical assessment info
- Actionable recommendations

✅ **Easy Integration**
- One-click download
- No configuration needed
- Browser-compatible PDF

✅ **Fleet Overview**
- Executive summary
- Comparative statistics
- Overall health status

## Troubleshooting

### PDF button doesn't download
1. Clear browser cache
2. Refresh the page
3. Run analysis again
4. Try downloading again

### Report is empty/blank
1. Ensure analysis has completed
2. Check browser console for errors
3. Verify API is running (port 5000)

### Flask server shows errors
1. Install reportlab: `pip install reportlab>=4.0.0`
2. Restart the Flask server
3. Try again

## Dashboard Buttons Overview

| Button | Action | When to Use |
|--------|--------|-----------|
| 📊 Load Real Data | Load CALCE dataset | Before analysis |
| 🔍 Run Analysis | Run all 5 agents | After loading data |
| 📥 Download PDF Report | Generate & download PDF | After analysis |
| 🗑️ Clear | Clear all data/results | Start fresh |

## File Naming

Downloaded PDFs are named with timestamp:
```
battery_report_20240115_143045.pdf
```
- `20240115` = Date (YYYYMMDD)
- `143045` = Time (HHMMSS)

## API Integration

Want to integrate PDF generation into your own application?

```javascript
// JavaScript example
async function downloadReport() {
  const response = await fetch('http://localhost:5000/api/generate-report', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ assessments: data })
  });
  
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = 'battery_report.pdf';
  link.click();
}
```

```python
# Python example
import requests

response = requests.post(
    'http://localhost:5000/api/generate-report',
    json={'assessments': assessments_data}
)

with open('battery_report.pdf', 'wb') as f:
    f.write(response.content)
```

## Requirements

- Flask server running (port 5000)
- Modern web browser
- ReportLab 4.0+ (already installed)

## Performance

- Single battery: ~1-2 seconds
- 5 batteries: ~2-3 seconds
- 10+ batteries: ~3-5 seconds

## Learn More

For detailed information, see:
- [PDF_REPORT_GUIDE.md](PDF_REPORT_GUIDE.md) - Complete documentation
- [test_report_generator.py](test_report_generator.py) - Test/example code
- [src/utils/report_generator.py](src/utils/report_generator.py) - Source code

---

**Happy reporting! 📊**
