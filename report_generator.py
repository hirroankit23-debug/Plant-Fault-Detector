from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime


def generate_report(
    filename,
    prediction,
    health_score,
    confidence,
    status,
    recommendation,
    importance
):

    styles = getSampleStyleSheet()

    doc = SimpleDocTemplate("Health_Report.pdf")

    story = []

    story.append(Paragraph("<b>Chemical Process Health Report</b>", styles["Title"]))

    story.append(
        Paragraph(
            f"Generated : {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}",
            styles["Normal"]
        )
    )

    story.append(
        Paragraph(f"Input File : {filename}", styles["Normal"])
    )

    story.append(
        Paragraph(f"Predicted Condition : {prediction}", styles["Normal"])
    )

    story.append(
        Paragraph(f"Health Score : {health_score:.2f}", styles["Normal"])
    )

    story.append(
        Paragraph(f"Confidence : {confidence:.2f}%", styles["Normal"])
    )

    story.append(
        Paragraph(f"Plant Status : {status}", styles["Normal"])
    )

    story.append(
        Paragraph("<b>Operator Recommendation</b>", styles["Heading2"])
    )

    story.append(
        Paragraph(recommendation, styles["Normal"])
    )

    story.append(
        Paragraph("<b>Top 5 Important Variables</b>", styles["Heading2"])
    )

    for _, row in importance.head(5).iterrows():

        story.append(
            Paragraph(
                f"{row['Display']} : {row['Importance']:.4f}",
                styles["Normal"]
            )
        )

    doc.build(story)