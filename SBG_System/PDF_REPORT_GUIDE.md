# PDF Report Generation Feature

## Overview

The Smart Battery Guardian now includes comprehensive PDF report generation functionality. Users can download detailed battery assessment reports in PDF format directly from the web dashboard.

## Features

### Executive Summary
- Total batteries analyzed
- Average risk score across fleet
- Count of healthy, warning, and critical batteries
- Key findings and fleet health status

### Detailed Battery Assessments
Each battery in the report includes:
- **Overall Risk Assessment**
  - Risk score (percentage)
  - Risk level (Healthy, Caution, Warning, Critical)
  - Maintenance recommendation

- **Thermal Analysis**
  - Temperature readings
  - Thermal anomalies
  - Risk level and score

- **Acoustic Fault Detection**
  - Impedance rise
  - Voltage noise
  - Current spikes
  - Detected fault indicators

- **RUL Prediction**
  - Predicted remaining useful life (cycles)
  - Capacity fade percentage
  - Degradation trends

- **Anomaly Detection**
  - Number of anomalies detected
  - Reconstruction error metrics
  - Detected patterns and deviations

## Usage

### From the Dashboard

1. **Load Real Data**
   - Click "📊 Load Real Data" button
   - System loads CALCE battery dataset

2. **Run Analysis**
   - Click "🔍 Run Analysis" button
   - System analyzes batteries with all agents
   - Results display on dashboard

3. **Download PDF Report**
   - Click "📥 Download PDF Report" button
   - System generates comprehensive PDF
   - PDF downloads automatically to your computer

### PDF Endpoint

**Endpoint:** `POST /api/generate-report`

**Request Body:**
```json
{
  "assessments": [
    {
      "battery_id": "B0005",
      "timestamp": "2024-01-15 14:30:45",
      "overall": {
        "risk_score": 0.42,
        "risk_level": "CAUTION",
        "recommendation": "Monitor battery closely..."
      },
      "agents": {
        "thermal": {...},
        "acoustic": {...},
        "rul": {...},
        "anomaly": {...}
      }
    }
  ]
}
```

**Response:** PDF file (application/pdf)

### Programmatic Usage

```python
from src.utils.report_generator import create_battery_report

# Sample assessments and summary
assessments = [
    {
        "battery_id": "B0005",
        "timestamp": "2024-01-15 14:30:45",
        "overall": {"risk_score": 0.42, "risk_level": "CAUTION", ...},
        "agents": {...}
    }
]

summary = {
    "total_batteries": 1,
    "avg_risk_score": 0.42,
    "healthy_count": 0,
    "warning_count": 1,
    "critical_count": 0
}

# Generate PDF
pdf_buffer = create_battery_report(assessments, summary)

# Save to file
with open("report.pdf", "wb") as f:
    f.write(pdf_buffer.getvalue())
```

## Report Generator Class

**Module:** `src/utils/report_generator.py`

### BatteryReportGenerator

Main class for generating PDF reports.

**Methods:**

#### `__init__()`
Initialize the report generator with custom styles.

#### `generate_report(assessments, summary)`
Generate comprehensive PDF report.

**Parameters:**
- `assessments` (list): List of assessment dictionaries
- `summary` (dict): Summary statistics dictionary

**Returns:**
- `BytesIO`: PDF file buffer

**Example:**
```python
generator = BatteryReportGenerator()
pdf_buffer = generator.generate_report(assessments, summary)
```

### Helper Methods

#### `_create_title_page()`
Creates the report title page with system info and disclaimer.

#### `_create_executive_summary(summary)`
Creates executive summary section with key statistics.

#### `_create_assessment_page(assessment)`
Creates detailed assessment page for a single battery.

#### `_create_agent_section(agent_name, agent_data)`
Creates section for individual agent analysis results.

## Report Contents

### Page 1: Title Page
- System name and version
- Report generation timestamp
- System description
- Disclaimer

### Page 2: Executive Summary
- Summary statistics table
- Key findings
- Overall fleet health status
- Risk breakdown

### Pages 3+: Detailed Assessments
- One page per battery (or multiple pages for large assessments)
- Risk visualization and metrics
- Per-agent analysis with detailed results
- Recommendations and alerts

## Report Styling

### Colors
- **Blue (#667eea)**: Headers and highlights
- **Green**: Healthy batteries
- **Orange**: Caution/Warning status
- **Red**: Critical status
- **Gray**: Tables and secondary elements

### Fonts
- **Helvetica**: Standard body text
- **Helvetica-Bold**: Headers and emphasis
- **Italic**: Notes and disclaimers

### Layout
- Professional A4/Letter format
- 0.5" margins on all sides
- Organized sections with clear hierarchy
- Tables with alternating row colors
- Page breaks between sections

## Example Report Data

### Healthy Battery (B0007)
- Risk Score: 18%
- Risk Level: HEALTHY
- Status: No action needed, continue monitoring
- Thermal: 32.1°C, normal
- Acoustic: Low impedance rise (0.008Ω)
- RUL: 2,890 cycles remaining
- Anomaly: No anomalies detected

### Critical Battery (B0006)
- Risk Score: 78%
- Risk Level: CRITICAL
- Status: Immediate action required
- Thermal: 52.3°C, high temperature
- Acoustic: High impedance (0.124Ω), voltage noise, current spikes
- RUL: 340 cycles remaining, rapid fade
- Anomaly: 5 anomalies detected

## Testing

### Test Script

Run `test_report_generator.py` to verify PDF generation:

```bash
python test_report_generator.py
```

**Output:**
```
Testing Battery Report Generation
1. Creating report generator...
   ✓ Report generated successfully
2. Checking PDF buffer...
   ✓ PDF size: 10,289 bytes (10.0 KB)
3. Saving test PDF...
   ✓ Saved to: test_battery_report.pdf
4. Verifying file...
   ✓ File exists: 10,289 bytes
✓ PDF Generation Test PASSED
```

### Generated Test PDF
- File: `test_battery_report.pdf`
- Contains sample data for 3 batteries
- Demonstrates full report formatting
- Suitable for reviewing report layout and styling

## Integration Points

### Dashboard Integration
1. User clicks "📥 Download PDF Report" button
2. Dashboard collects latest assessment data
3. Calls `/api/generate-report` endpoint
4. Browser downloads PDF file

### Flask API
```python
@app.route('/api/generate-report', methods=['POST'])
def generate_report():
    data = request.get_json()
    assessments = data.get('assessments', [])
    
    # Calculate summary
    summary = {...}
    
    # Generate PDF
    pdf_buffer = create_battery_report(assessments, summary)
    
    # Return file
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f"battery_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    )
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'reportlab'"
**Solution:** Install reportlab
```bash
pip install reportlab>=4.0.0
```

### PDF file is empty or corrupted
**Possible causes:**
- Assessment data is not in expected format
- Required fields are missing from assessment dictionaries
- Memory issues with large datasets

**Solution:** Verify assessment data structure matches expected format.

### PDF download button doesn't appear
**Solution:** Clear browser cache and refresh dashboard

### Generated PDF has formatting issues
**Solution:** Update to latest reportlab version
```bash
pip install --upgrade reportlab
```

## Requirements

- ReportLab >= 4.0.0 (PDF generation)
- Pillow >= 9.0.0 (Image support - already installed)
- Python >= 3.9

## Performance

- **Single Battery Report:** ~1-2 seconds
- **5 Battery Report:** ~2-3 seconds
- **10+ Battery Report:** ~3-5 seconds
- **PDF File Size:** 10-15 KB per battery

## Future Enhancements

Potential improvements for future versions:

1. **Chart Integration**
   - Historical trend charts
   - Risk score evolution graphs
   - Temperature/capacity fade visualization

2. **Custom Branding**
   - User logo support
   - Custom company information
   - Configurable colors/styling

3. **Batch Reports**
   - Generate reports for multiple batteries
   - Combine into single document
   - Archive reports with metadata

4. **Email Delivery**
   - Direct email delivery of reports
   - Scheduled daily/weekly reports
   - Alert-triggered reports

5. **Advanced Analytics**
   - Statistical summaries
   - Fleet comparison metrics
   - Predictive degradation trends

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review test script output
3. Examine Flask server logs
4. Check browser console for JavaScript errors

## License

Same as Smart Battery Guardian system
