# ============================================
# TECHTRAP - AI Neuro-Motor Doctor Report
# ============================================

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.colors import HexColor
import matplotlib.pyplot as plt
import qrcode
import os
from datetime import datetime

# ============================================
# COLORS (HEX ONLY – IMPORTANT)
# ============================================

PRIMARY_COLOR = "#40246c"
SUCCESS_COLOR = "#1abc9c"
WARNING_COLOR = "#f39c12"
DANGER_COLOR  = "#e74c3c"
GRAY_COLOR    = "#555555"

# ============================================
# Helper: Score Color
# ============================================

def score_color(level):
    if level == "Normal":
        return SUCCESS_COLOR
    elif level == "Mild Delay":
        return WARNING_COLOR
    else:
        return DANGER_COLOR

# ============================================
# Generate Doctor PDF Report
# ============================================

def generate_doctor_report_pdf(child_info, game_metrics, ai_result):

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"TECHTRAP_Doctor_Report_{timestamp}.pdf"

    pdf = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    content = []

    # ---------- Styles ----------
    title_style = ParagraphStyle(
        "Title",
        fontSize=24,
        alignment=TA_CENTER,
        textColor=HexColor(PRIMARY_COLOR),
        spaceAfter=16
    )

    subtitle_style = ParagraphStyle(
        "SubTitle",
        fontSize=14,
        alignment=TA_CENTER,
        textColor=HexColor(GRAY_COLOR),
        spaceAfter=20
    )

    section_style = ParagraphStyle(
        "Section",
        fontSize=15,
        textColor=HexColor(PRIMARY_COLOR),
        spaceBefore=20,
        spaceAfter=10
    )

    normal_style = styles["Normal"]

    # ---------- Header ----------
    content.append(Paragraph("<b>TECHTRAP</b>", title_style))
    content.append(Paragraph(
        "AI-Powered Neuro-Motor Assessment Report",
        subtitle_style
    ))
    content.append(Spacer(1, 10))

    # ---------- Child Info ----------
    content.append(Paragraph("👶 Child Information", section_style))
    content.append(Paragraph(f"Name: <b>{child_info.get('name')}</b>", normal_style))
    content.append(Paragraph(f"Age: {child_info.get('age')}", normal_style))
    content.append(Paragraph(f"Session ID: {child_info.get('session_id')}", normal_style))

    # ---------- Game Metrics ----------
    content.append(Paragraph("🎮 Game Performance Metrics", section_style))
    for k, v in game_metrics.items():
        content.append(
            Paragraph(f"{k.replace('_',' ').title()}: <b>{v}</b>", normal_style)
        )

    # ---------- AI Result ----------
    color_hex = score_color(ai_result["risk_level"])

    content.append(Paragraph("🧠 AI Neuro-Motor Analysis (MindSpore)", section_style))

    content.append(Paragraph(
        f"""
        <para>
            <b>Neuro-Motor Score:</b>
            <font color="{color_hex}" size="18">
                {ai_result['neuro_motor_score']} / 100
            </font>
        </para>
        """,
        normal_style
    ))

    content.append(Paragraph(
        f"Risk Level: <b>{ai_result['risk_level']}</b>",
        normal_style
    ))

    # ---------- AI Explanation ----------
    content.append(Paragraph("🤖 AI Clinical Interpretation", section_style))
    content.append(Paragraph(
        interpret_result(ai_result["risk_level"]),
        normal_style
    ))

    # ---------- Chart ----------
    chart_path = "neuro_motor_chart.png"
    generate_chart(game_metrics, ai_result["neuro_motor_score"], chart_path)
    content.append(Spacer(1, 20))
    content.append(Image(chart_path, width=420, height=260))

    # ---------- QR Code ----------
    qr_path = "techtrap_qr.png"
    generate_qr(qr_path)
    content.append(Spacer(1, 20))
    content.append(Image(qr_path, width=100, height=100))
    content.append(Paragraph(
        "Scan for digital session & AI model traceability",
        ParagraphStyle("qr", alignment=TA_CENTER, fontSize=9)
    ))

    # ---------- Footer ----------
    content.append(Spacer(1, 30))
    content.append(Paragraph(
        "Generated automatically by TECHTRAP AI Medical Platform",
        ParagraphStyle("footer", alignment=TA_CENTER, fontSize=9)
    ))

    pdf.build(content)

    # Cleanup
    for f in [chart_path, qr_path]:
        if os.path.exists(f):
            os.remove(f)

    return filename

# ============================================
# Chart
# ============================================

def generate_chart(metrics, score, path):
    labels = ["Speed", "Stability", "Reaction", "Error Rate"]
    values = [
        metrics.get("avg_speed", 0),
        metrics.get("stability", 0),
        metrics.get("reaction_time", 0),
        metrics.get("error_rate", 0),
    ]

    plt.figure(figsize=(6, 4))
    plt.bar(labels, values)
    plt.axhline(y=score / 25, linestyle="--", label="AI Reference")
    plt.title("Neuro-Motor Performance Overview")
    plt.legend()
    plt.tight_layout()
    plt.savefig(path)
    plt.close()

# ============================================
# QR Code
# ============================================

def generate_qr(path):
    qr = qrcode.make("https://techtrap.ai/medical-report")
    qr.save(path)

# ============================================
# Interpretation
# ============================================

def interpret_result(level):
    if level == "Normal":
        return (
            "The AI model indicates age-appropriate neuro-motor development. "
            "No immediate clinical concerns detected."
        )
    elif level == "Mild Delay":
        return (
            "The AI analysis suggests mild neuro-motor delay. "
            "Supervised exercises and periodic monitoring are recommended."
        )
    else:
        return (
            "The AI model detected potential neuro-motor difficulties. "
            "Further clinical evaluation is strongly advised."
        )

# ============================================
# Alias (DO NOT REMOVE)
# ============================================

def generate_doctor_pdf(child_info, game_metrics, ai_result):
    return generate_doctor_report_pdf(
        child_info=child_info,
        game_metrics=game_metrics,
        ai_result=ai_result
    )
