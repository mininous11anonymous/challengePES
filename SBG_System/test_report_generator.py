"""Test PDF Report Generation"""

import json
import os
from src.utils.report_generator import create_battery_report

# Sample assessment data
sample_assessments = [
    {
        "battery_id": "B0005",
        "timestamp": "2024-01-15 14:30:45",
        "overall": {
            "risk_score": 0.42,
            "risk_level": "CAUTION",
            "recommendation": "Monitor battery closely. Schedule maintenance within 30 days."
        },
        "agents": {
            "thermal": {
                "risk_level": "HEALTHY",
                "risk_score": 0.25,
                "temperature": 38.5,
                "anomalies": []
            },
            "acoustic": {
                "risk_level": "CAUTION",
                "risk_score": 0.52,
                "fault_indicators": {
                    "impedance_rise": 0.038,
                    "voltage_noise": 0.00234,
                    "current_spikes": 0.156
                },
                "anomalies": ["Impedance rise detected"]
            },
            "rul": {
                "risk_level": "HEALTHY",
                "risk_score": 0.35,
                "predicted_rul_cycles": 1250,
                "capacity_fade": 0.15,
                "anomalies": []
            },
            "anomaly": {
                "risk_level": "HEALTHY",
                "risk_score": 0.20,
                "anomalies_detected": 0,
                "reconstruction_error": 0.0234,
                "anomalies": []
            }
        }
    },
    {
        "battery_id": "B0006",
        "timestamp": "2024-01-15 14:35:20",
        "overall": {
            "risk_score": 0.78,
            "risk_level": "CRITICAL",
            "recommendation": "IMMEDIATE ACTION REQUIRED. Battery requires urgent inspection and possible replacement."
        },
        "agents": {
            "thermal": {
                "risk_level": "WARNING",
                "risk_score": 0.68,
                "temperature": 52.3,
                "anomalies": ["High temperature detected"]
            },
            "acoustic": {
                "risk_level": "CRITICAL",
                "risk_score": 0.85,
                "fault_indicators": {
                    "impedance_rise": 0.124,
                    "voltage_noise": 0.0089,
                    "current_spikes": 0.456
                },
                "anomalies": ["High impedance rise", "Voltage noise", "Current spikes"]
            },
            "rul": {
                "risk_level": "WARNING",
                "risk_score": 0.72,
                "predicted_rul_cycles": 340,
                "capacity_fade": 0.45,
                "anomalies": ["Rapid capacity fade"]
            },
            "anomaly": {
                "risk_level": "CRITICAL",
                "risk_score": 0.91,
                "anomalies_detected": 5,
                "reconstruction_error": 0.1876,
                "anomalies": ["Pattern deviation", "Sudden change", "Outlier detected"]
            }
        }
    },
    {
        "battery_id": "B0007",
        "timestamp": "2024-01-15 14:40:10",
        "overall": {
            "risk_score": 0.18,
            "risk_level": "HEALTHY",
            "recommendation": "Battery is operating normally. Continue regular monitoring."
        },
        "agents": {
            "thermal": {
                "risk_level": "HEALTHY",
                "risk_score": 0.10,
                "temperature": 32.1,
                "anomalies": []
            },
            "acoustic": {
                "risk_level": "HEALTHY",
                "risk_score": 0.15,
                "fault_indicators": {
                    "impedance_rise": 0.008,
                    "voltage_noise": 0.00089,
                    "current_spikes": 0.034
                },
                "anomalies": []
            },
            "rul": {
                "risk_level": "HEALTHY",
                "risk_score": 0.22,
                "predicted_rul_cycles": 2890,
                "capacity_fade": 0.05,
                "anomalies": []
            },
            "anomaly": {
                "risk_level": "HEALTHY",
                "risk_score": 0.08,
                "anomalies_detected": 0,
                "reconstruction_error": 0.0045,
                "anomalies": []
            }
        }
    }
]

sample_summary = {
    "total_batteries": 3,
    "avg_risk_score": 0.46,
    "healthy_count": 1,
    "warning_count": 1,
    "critical_count": 1
}

def test_report_generation():
    """Test PDF report generation"""
    print("\n" + "="*60)
    print("Testing Battery Report Generation")
    print("="*60)
    
    try:
        print("\n1. Creating report generator...")
        pdf_buffer = create_battery_report(sample_assessments, sample_summary)
        print("   ✓ Report generated successfully")
        
        print("\n2. Checking PDF buffer...")
        pdf_size = len(pdf_buffer.getvalue())
        print(f"   ✓ PDF size: {pdf_size:,} bytes ({pdf_size/1024:.1f} KB)")
        
        print("\n3. Saving test PDF...")
        output_path = "test_battery_report.pdf"
        with open(output_path, 'wb') as f:
            f.write(pdf_buffer.getvalue())
        print(f"   ✓ Saved to: {output_path}")
        
        print("\n4. Verifying file...")
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"   ✓ File exists: {file_size:,} bytes")
        
        print("\n" + "="*60)
        print("✓ PDF Generation Test PASSED")
        print("="*60 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_report_generation()
    exit(0 if success else 1)
