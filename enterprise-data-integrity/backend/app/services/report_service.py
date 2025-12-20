"""
Report Service - Module 4
Generates reports and recommendations
"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import os


class ReportService:
    """Service for generating reports"""

    def __init__(self, output_dir: str = "/tmp/reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate_executive_summary_pdf(
        self, run_data: Dict[str, Any], issues: List[Dict], connector_name: str
    ) -> str:
        """
        Generate Executive Summary PDF report

        Args:
            run_data: Run execution data
            issues: List of issues found
            connector_name: Name of the connector

        Returns:
            Path to generated PDF file
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"executive_summary_{timestamp}.pdf"
        filepath = os.path.join(self.output_dir, filename)

        # Create PDF
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Heading1"],
            fontSize=24,
            textColor=colors.HexColor("#1a1a1a"),
            spaceAfter=30,
            alignment=TA_CENTER,
        )

        heading_style = ParagraphStyle(
            "CustomHeading",
            parent=styles["Heading2"],
            fontSize=16,
            textColor=colors.HexColor("#2c3e50"),
            spaceAfter=12,
            spaceBefore=12,
        )

        # Title
        story.append(Paragraph("Data Integrity Assessment Report", title_style))
        story.append(Spacer(1, 0.2 * inch))

        # Executive Summary Section
        story.append(Paragraph("Executive Summary", heading_style))

        summary_text = f"""
        This report provides a comprehensive assessment of data quality and integration health
        for {connector_name}. The analysis was conducted on {datetime.utcnow().strftime('%B %d, %Y')}.
        """
        story.append(Paragraph(summary_text, styles["Normal"]))
        story.append(Spacer(1, 0.3 * inch))

        # Key Metrics
        story.append(Paragraph("Key Metrics", heading_style))

        metrics_data = [
            ["Metric", "Value"],
            ["Total Records Analyzed", f"{run_data.get('total_records', 0):,}"],
            ["Rules Executed", str(run_data.get("rules_executed", 0))],
            ["Rules Passed", str(run_data.get("rules_passed", 0))],
            ["Rules Failed", str(run_data.get("rules_failed", 0))],
            ["Total Issues Found", str(run_data.get("total_issues", 0))],
        ]

        metrics_table = Table(metrics_data, colWidths=[3.5 * inch, 2 * inch])
        metrics_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#34495e")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 12),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )
        story.append(metrics_table)
        story.append(Spacer(1, 0.3 * inch))

        # Issues by Severity
        story.append(Paragraph("Issues by Severity", heading_style))

        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for issue in issues:
            severity = issue.get("severity", "low")
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        severity_data = [
            ["Severity", "Count"],
            ["Critical", str(severity_counts.get("critical", 0))],
            ["High", str(severity_counts.get("high", 0))],
            ["Medium", str(severity_counts.get("medium", 0))],
            ["Low", str(severity_counts.get("low", 0))],
        ]

        severity_table = Table(severity_data, colWidths=[3.5 * inch, 2 * inch])
        severity_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#34495e")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 12),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )
        story.append(severity_table)
        story.append(Spacer(1, 0.3 * inch))

        # Top Issues
        story.append(Paragraph("Top Issues Requiring Immediate Attention", heading_style))

        critical_issues = [
            issue for issue in issues if issue.get("severity") in ["critical", "high"]
        ][:5]

        if critical_issues:
            for idx, issue in enumerate(critical_issues, 1):
                issue_text = f"""
                <b>{idx}. {issue.get('title', 'Unknown Issue')}</b><br/>
                Severity: {issue.get('severity', 'N/A').upper()}<br/>
                Description: {issue.get('description', 'No description')}
                """
                story.append(Paragraph(issue_text, styles["Normal"]))
                story.append(Spacer(1, 0.1 * inch))
        else:
            story.append(Paragraph("No critical issues found.", styles["Normal"]))

        story.append(Spacer(1, 0.3 * inch))

        # Recommendations
        story.append(Paragraph("Recommendations", heading_style))

        recommendations = self._generate_recommendations(run_data, issues)
        for idx, rec in enumerate(recommendations, 1):
            story.append(Paragraph(f"{idx}. {rec}", styles["Normal"]))
            story.append(Spacer(1, 0.1 * inch))

        # Build PDF
        doc.build(story)

        return filepath

    def _generate_recommendations(
        self, run_data: Dict[str, Any], issues: List[Dict]
    ) -> List[str]:
        """Generate recommendations based on issues found"""
        recommendations = []

        total_issues = run_data.get("total_issues", 0)

        if total_issues == 0:
            recommendations.append(
                "Data quality is excellent. Continue monitoring to maintain standards."
            )
            return recommendations

        # Check for duplicates
        if any("duplicate" in issue.get("rule_name", "").lower() for issue in issues):
            recommendations.append(
                "Implement duplicate detection and removal process in upstream systems"
            )
            recommendations.append(
                "Review data entry procedures to prevent duplicate creation"
            )

        # Check for missing fields
        if any("missing" in issue.get("rule_name", "").lower() for issue in issues):
            recommendations.append(
                "Make mandatory fields required in source systems to prevent null values"
            )
            recommendations.append(
                "Implement data validation at point of entry"
            )

        # Check for hierarchy issues
        if any("hierarchy" in issue.get("rule_name", "").lower() for issue in issues):
            recommendations.append(
                "Audit and correct organizational hierarchy data"
            )
            recommendations.append(
                "Implement hierarchy validation rules in HR system"
            )

        # General recommendations
        if total_issues > 100:
            recommendations.append(
                "Schedule data cleanup initiative to address large volume of issues"
            )
            recommendations.append(
                "Consider implementing automated data quality monitoring"
            )

        recommendations.append(
            "Set up weekly automated reports to track data quality trends"
        )

        return recommendations

    def generate_trend_analysis(
        self, historical_runs: List[Dict], days: int = 30
    ) -> Dict[str, Any]:
        """
        Generate trend analysis for the past N days

        Args:
            historical_runs: List of historical run data
            days: Number of days to analyze

        Returns:
            Trend analysis data
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        recent_runs = [
            run
            for run in historical_runs
            if datetime.fromisoformat(run.get("created_at", "")) > cutoff_date
        ]

        if not recent_runs:
            return {
                "period_days": days,
                "total_runs": 0,
                "avg_issues": 0,
                "trend": "insufficient_data",
            }

        total_issues = sum(run.get("total_issues", 0) for run in recent_runs)
        avg_issues = total_issues / len(recent_runs) if recent_runs else 0

        # Simple trend: compare first half vs second half
        mid_point = len(recent_runs) // 2
        first_half_avg = (
            sum(run.get("total_issues", 0) for run in recent_runs[:mid_point])
            / mid_point
            if mid_point > 0
            else 0
        )
        second_half_avg = (
            sum(run.get("total_issues", 0) for run in recent_runs[mid_point:])
            / (len(recent_runs) - mid_point)
            if (len(recent_runs) - mid_point) > 0
            else 0
        )

        if second_half_avg < first_half_avg * 0.9:
            trend = "improving"
        elif second_half_avg > first_half_avg * 1.1:
            trend = "degrading"
        else:
            trend = "stable"

        return {
            "period_days": days,
            "total_runs": len(recent_runs),
            "total_issues": total_issues,
            "avg_issues": round(avg_issues, 2),
            "trend": trend,
            "first_half_avg": round(first_half_avg, 2),
            "second_half_avg": round(second_half_avg, 2),
        }
