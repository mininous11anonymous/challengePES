"""PDF Report Generation for Battery Assessments"""

import io
import json
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    PageBreak,
    Image,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


class BatteryReportGenerator:
    """Generate comprehensive PDF reports for battery assessments"""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()

    def _create_custom_styles(self):
        """Create custom paragraph styles"""
        self.styles.add(
            ParagraphStyle(
                name="CustomTitle",
                parent=self.styles["Heading1"],
                fontSize=24,
                textColor=colors.HexColor("#667eea"),
                spaceAfter=30,
                alignment=TA_CENTER,
                fontName="Helvetica-Bold",
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="CustomHeading",
                parent=self.styles["Heading2"],
                fontSize=14,
                textColor=colors.HexColor("#667eea"),
                spaceAfter=12,
                spaceBefore=12,
                fontName="Helvetica-Bold",
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="CustomBody",
                parent=self.styles["BodyText"],
                fontSize=11,
                spaceAfter=6,
            )
        )

    def generate_report(self, assessments, summary):
        """
        Generate a comprehensive PDF report

        Args:
            assessments: List of assessment dictionaries
            summary: Summary dictionary with overall statistics

        Returns:
            BytesIO object containing PDF
        """
        pdf_buffer = io.BytesIO()

        doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=letter,
            rightMargin=0.5 * inch,
            leftMargin=0.5 * inch,
            topMargin=0.5 * inch,
            bottomMargin=0.5 * inch,
        )

        story = []

        # Title Page
        story.extend(self._create_title_page())
        story.append(PageBreak())

        # Executive Summary
        story.extend(self._create_executive_summary(summary))
        story.append(PageBreak())

        # Detailed Assessments
        for i, assessment in enumerate(assessments):
            story.extend(self._create_assessment_page(assessment))
            if i < len(assessments) - 1:
                story.append(PageBreak())

        # Build PDF
        doc.build(story)
        pdf_buffer.seek(0)
        return pdf_buffer

    def _create_title_page(self):
        """Create title page"""
        story = []

        # Logo/Header
        story.append(Spacer(1, 1 * inch))
        story.append(
            Paragraph(
                "🔋 Smart Battery Guardian",
                self.styles["CustomTitle"],
            )
        )
        story.append(
            Paragraph(
                "Comprehensive Battery Health Assessment Report",
                self.styles["Heading2"],
            )
        )

        story.append(Spacer(1, 0.5 * inch))

        # Date and timestamp
        timestamp = datetime.now().strftime("%B %d, %Y at %H:%M:%S")
        story.append(
            Paragraph(
                f"<b>Report Generated:</b> {timestamp}",
                self.styles["Normal"],
            )
        )
        story.append(Spacer(1, 0.3 * inch))

        # System info
        story.append(
            Paragraph(
                "<b>System:</b> AI-Powered Multi-Agent Battery Monitoring Platform",
                self.styles["Normal"],
            )
        )
        story.append(
            Paragraph(
                "<b>Version:</b> 1.0 Production",
                self.styles["Normal"],
            )
        )

        story.append(Spacer(1, 0.5 * inch))

        # Disclaimer
        story.append(
            Paragraph(
                "<i>This report contains confidential assessment data and risk predictions "
                "based on AI analysis. Recommendations should be reviewed by qualified "
                "battery management personnel.</i>",
                self.styles["Italic"],
            )
        )

        return story

    def _create_executive_summary(self, summary):
        """Create executive summary section"""
        story = []

        story.append(Paragraph("Executive Summary", self.styles["CustomHeading"]))
        story.append(Spacer(1, 0.2 * inch))

        # Summary statistics table
        summary_data = [
            ["Metric", "Value"],
            ["Batteries Analyzed", str(summary.get("total_batteries", 0))],
            ["Average Risk Score", f"{summary.get('avg_risk_score', 0)*100:.1f}%"],
            ["Healthy Batteries", str(summary.get("healthy_count", 0))],
            ["Batteries with Warning", str(summary.get("warning_count", 0))],
            ["Critical Batteries", str(summary.get("critical_count", 0))],
        ]

        table = Table(summary_data, colWidths=[3 * inch, 2 * inch])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#667eea")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 12),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 1), (-1, -1), 11),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                ]
            )
        )

        story.append(table)
        story.append(Spacer(1, 0.2 * inch))

        # Key findings
        story.append(Paragraph("Key Findings", self.styles["Heading3"]))
        story.append(Spacer(1, 0.1 * inch))

        avg_risk = summary.get("avg_risk_score", 0)
        if avg_risk < 0.3:
            health_status = "HEALTHY - All batteries operating normally"
            color = "green"
        elif avg_risk < 0.5:
            health_status = "CAUTION - Some batteries show minor degradation"
            color = "orange"
        elif avg_risk < 0.7:
            health_status = "WARNING - Several batteries need attention"
            color = "darkorange"
        else:
            health_status = "CRITICAL - Immediate action required"
            color = "red"

        story.append(
            Paragraph(
                f"<font color='{color}'><b>Overall Fleet Status: {health_status}</b></font>",
                self.styles["Normal"],
            )
        )

        story.append(Spacer(1, 0.1 * inch))
        story.append(
            Paragraph(
                f"The analyzed battery fleet shows an average risk level of "
                f"<b>{avg_risk*100:.1f}%</b>. {summary.get('healthy_count', 0)} batteries "
                f"are in good condition, while {summary.get('critical_count', 0)} require "
                f"immediate attention.",
                self.styles["CustomBody"],
            )
        )

        return story

    def _create_assessment_page(self, assessment):
        """Create a detailed assessment page for one battery"""
        story = []

        battery_id = assessment.get("battery_id", "Unknown")
        overall = assessment.get("overall", {})
        agents = assessment.get("agents", {})

        # Battery header
        story.append(
            Paragraph(
                f"Battery Assessment: {battery_id}",
                self.styles["CustomHeading"],
            )
        )

        timestamp = assessment.get("timestamp", "Unknown")
        story.append(
            Paragraph(
                f"<i>Assessment Date: {timestamp}</i>",
                self.styles["Normal"],
            )
        )

        story.append(Spacer(1, 0.2 * inch))

        # Overall Risk Summary
        story.append(Paragraph("Overall Risk Assessment", self.styles["Heading3"]))

        risk_score = overall.get("risk_score", 0)
        risk_level = overall.get("risk_level", "UNKNOWN")
        recommendation = overall.get("recommendation", "No recommendation")

        # Risk level color
        if risk_level == "HEALTHY":
            color = "#4CAF50"
        elif risk_level == "CAUTION":
            color = "#FFC107"
        elif risk_level == "WARNING":
            color = "#FF5722"
        else:
            color = "#F44336"

        risk_table_data = [
            ["Overall Risk Score", f"{risk_score*100:.1f}%"],
            ["Risk Level", f"<font color='{color}'><b>{risk_level}</b></font>"],
            ["Recommendation", recommendation],
        ]

        risk_table = Table(risk_table_data, colWidths=[2.5 * inch, 2.5 * inch])
        risk_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.lightgrey),
                    ("GRID", (0, 0), (-1, -1), 1, colors.grey),
                    ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]
            )
        )

        story.append(risk_table)
        story.append(Spacer(1, 0.2 * inch))

        # Detailed Agent Analysis
        story.append(Paragraph("Detailed Agent Analysis", self.styles["Heading3"]))
        story.append(Spacer(1, 0.1 * inch))

        # Thermal Agent
        if "thermal" in agents:
            story.extend(self._create_agent_section("Thermal Analysis", agents["thermal"]))
            story.append(Spacer(1, 0.1 * inch))

        # Acoustic Agent
        if "acoustic" in agents:
            story.extend(
                self._create_agent_section("Acoustic Fault Detection", agents["acoustic"])
            )
            story.append(Spacer(1, 0.1 * inch))

        # RUL Agent
        if "rul" in agents:
            story.extend(self._create_agent_section("RUL Prediction", agents["rul"]))
            story.append(Spacer(1, 0.1 * inch))

        # Anomaly Agent
        if "anomaly" in agents:
            story.extend(
                self._create_agent_section("Anomaly Detection", agents["anomaly"])
            )

        return story

    def _create_agent_section(self, agent_name, agent_data):
        """Create a section for a single agent"""
        story = []

        story.append(Paragraph(f"<b>{agent_name}</b>", self.styles["Heading4"]))

        # Agent metrics table
        metrics_data = [["Metric", "Value"]]

        risk_level = agent_data.get("risk_level", "Unknown")
        risk_score = agent_data.get("risk_score", 0)

        metrics_data.append(["Risk Level", risk_level])
        metrics_data.append(["Risk Score", f"{risk_score*100:.1f}%"])

        # Add agent-specific metrics
        if agent_name == "Thermal Analysis" and "temperature" in agent_data:
            metrics_data.append(["Temperature", f"{agent_data['temperature']:.1f}°C"])

        if agent_name == "Acoustic Fault Detection" and "fault_indicators" in agent_data:
            indicators = agent_data["fault_indicators"]
            metrics_data.append(
                [
                    "Impedance Rise",
                    f"{indicators.get('impedance_rise', 0):.3f} Ω",
                ]
            )
            metrics_data.append(
                [
                    "Voltage Noise",
                    f"{indicators.get('voltage_noise', 0):.4f}",
                ]
            )
            metrics_data.append(
                [
                    "Current Spikes",
                    f"{indicators.get('current_spikes', 0):.3f}",
                ]
            )

        if agent_name == "RUL Prediction":
            if "predicted_rul_cycles" in agent_data:
                metrics_data.append(
                    ["Predicted RUL", f"{agent_data['predicted_rul_cycles']} cycles"]
                )
            if "capacity_fade" in agent_data:
                metrics_data.append(
                    [
                        "Capacity Fade",
                        f"{agent_data['capacity_fade']*100:.1f}%",
                    ]
                )

        if agent_name == "Anomaly Detection":
            if "anomalies_detected" in agent_data:
                metrics_data.append(
                    [
                        "Anomalies Detected",
                        str(agent_data["anomalies_detected"]),
                    ]
                )
            if "reconstruction_error" in agent_data:
                metrics_data.append(
                    [
                        "Reconstruction Error",
                        f"{agent_data['reconstruction_error']:.4f}",
                    ]
                )

        # Add anomalies if present
        if "anomalies" in agent_data and agent_data["anomalies"]:
            anomalies_text = ", ".join(agent_data["anomalies"])
            metrics_data.append(["Detected Issues", anomalies_text])

        metrics_table = Table(metrics_data, colWidths=[2.5 * inch, 2.5 * inch])
        metrics_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#667eea")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                    ("GRID", (0, 0), (-1, -1), 1, colors.grey),
                    ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 1), (-1, -1), 9),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                ]
            )
        )

        story.append(metrics_table)
        return story


def create_battery_report(assessments, summary):
    """
    Convenience function to generate a battery report

    Args:
        assessments: List of assessment dictionaries
        summary: Summary dictionary

    Returns:
        BytesIO object containing PDF
    """
    generator = BatteryReportGenerator()
    return generator.generate_report(assessments, summary)
