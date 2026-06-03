from __future__ import annotations

from datetime import date
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


BRAND_GREEN = colors.HexColor("#154734")
SAFFRON = colors.HexColor("#C56A1A")
SOFT_GOLD = colors.HexColor("#F5E7BE")
INK = colors.HexColor("#1F2A24")
MUTED = colors.HexColor("#5D665F")


def build_pdf(chart: dict) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=42,
        leftMargin=42,
        topMargin=42,
        bottomMargin=42,
        title=f"Sattvic Gyaan Basic Vedic Report - {chart['birth'].name}",
        author="Sattvic Gyaan",
    )
    story = []
    styles = _styles()

    _cover(story, styles, chart)
    story.append(PageBreak())
    _birth_summary(story, styles, chart)
    _core_chart(story, styles, chart)
    _planet_table(story, styles, chart)
    _nakshatra_section(story, styles, chart)
    _vimshottari_dasha_section(story, styles, chart)
    _dosha_section(story, styles, chart)
    _predictions(story, styles, chart)
    _disclaimer(story, styles)

    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
    return buffer.getvalue()


def _cover(story: list, styles: dict, chart: dict) -> None:
    birth = chart["birth"]
    story.append(Spacer(1, 1.0 * inch))
    story.append(Paragraph("Sattvic Gyaan", styles["brand"]))
    story.append(Spacer(1, 0.25 * inch))
    story.append(Paragraph("Basic Vedic Astrology Report", styles["cover_title"]))
    story.append(Spacer(1, 0.35 * inch))
    story.append(Paragraph(f"Prepared for {birth.name}", styles["cover_name"]))
    story.append(Spacer(1, 0.5 * inch))
    story.append(
        Paragraph(
            "A concise spiritual astrology report based on Nirayana Vedic calculations "
            "using Lahiri/Chitrapaksha ayanamsa.",
            styles["center_body"],
        )
    )
    story.append(Spacer(1, 0.75 * inch))
    story.append(
        _info_table(
            [
                ["Birth Date", birth.birth_date.strftime("%d %b %Y")],
                ["Birth Time", birth.birth_time.strftime("%H:%M")],
                ["Birth Place", birth.place],
                ["Coordinates", f"{birth.latitude:.4f}, {birth.longitude:.4f}"],
                ["Timezone", f"UTC{birth.timezone_offset:+.2f}"],
            ]
        )
    )


def _birth_summary(story: list, styles: dict, chart: dict) -> None:
    birth = chart["birth"]
    story.append(Paragraph("Birth Details", styles["h1"]))
    story.append(
        _info_table(
            [
                ["Name", birth.name],
                ["Gender", birth.gender or "Not specified"],
                ["Date of Birth", birth.birth_date.strftime("%d %B %Y")],
                ["Time of Birth", birth.birth_time.strftime("%H:%M")],
                ["Place of Birth", birth.place],
                ["Latitude", f"{birth.latitude:.4f}"],
                ["Longitude", f"{birth.longitude:.4f}"],
                ["Timezone", f"UTC{birth.timezone_offset:+.2f}"],
                ["UTC Time Used", chart["utc_datetime"].strftime("%d %b %Y, %H:%M UTC")],
                ["Calculation Basis", chart["calculation_basis"]],
                ["Calculation Engine", chart["calculation_engine"]],
            ]
        )
    )
    story.append(Spacer(1, 0.25 * inch))


def _core_chart(story: list, styles: dict, chart: dict) -> None:
    story.append(Paragraph("Core Chart Snapshot", styles["h1"]))
    panchang = chart["panchang"]
    story.append(
        _info_table(
            [
                ["Lagna / Ascendant", f"{chart['ascendant']['sign']} {chart['ascendant']['degree']}"],
                ["Moon Sign / Rashi", chart["rashi"]],
                ["Sun Sign", chart["sun_sign"]],
                ["Janma Nakshatra", chart["nakshatra"]],
                ["Nakshatra Pada", str(chart["nakshatra_pada"])],
                ["Tithi", panchang["tithi"]],
                ["Paksha", panchang["paksha"]],
                ["Yoga", panchang["yoga"]],
                ["Karana", panchang["karana"]],
            ]
        )
    )
    story.append(Spacer(1, 0.25 * inch))


def _planet_table(story: list, styles: dict, chart: dict) -> None:
    story.append(Paragraph("Planetary Positions", styles["h1"]))
    rows = [["Graha", "Sign", "Degree", "House", "Nakshatra", "Pada"]]
    for row in chart["planets"]:
        rows.append(
            [
                row["planet"],
                row["sign"],
                row["degree"],
                str(row["house"]),
                row["nakshatra"],
                str(row["pada"]),
            ]
        )
    table = Table(rows, colWidths=[72, 82, 75, 48, 112, 40])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), BRAND_GREEN),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.6),
                ("TEXTCOLOR", (0, 1), (-1, -1), INK),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#CDD6CE")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7FAF7")]),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(table)


def _nakshatra_section(story: list, styles: dict, chart: dict) -> None:
    story.append(Paragraph("Janma Nakshatra Details", styles["h1"]))
    nak = chart["nakshatra"]
    pada = chart["nakshatra_pada"]
    det = chart.get("nakshatra_details", {})
    rows = [
        ["Nakshatra", f"{nak} (Pada {pada})"],
        ["Nakshatra Swami (Lord)", det.get("lord", "—")],
        ["Adhidevata (Deity)", det.get("deity", "—")],
        ["Symbol", det.get("symbol", "—")],
        ["Gana", det.get("gana", "—")],
        ["Varna", det.get("varna", "—")],
        ["Nature / Quality", det.get("quality", "—")],
    ]
    story.append(_info_table(rows))
    story.append(Spacer(1, 0.12 * inch))

    # Brief spiritual significance paragraph
    gana = det.get("gana", "")
    lord = det.get("lord", "")
    deity = det.get("deity", "")
    story.append(
        Paragraph(
            f"{nak} nakshatra, ruled by {lord} and presided over by {deity}, belongs to the "
            f"{gana} Gana. Those born under this nakshatra carry the qualities of their ruling "
            f"planet in a subtle but persistent way. The symbol and deity together define the "
            f"soul's primary dharmic impulse in this lifetime.",
            styles["body"],
        )
    )
    story.append(Spacer(1, 0.25 * inch))


def _vimshottari_dasha_section(story: list, styles: dict, chart: dict) -> None:
    story.append(Paragraph("Vimshottari Dasha (120-Year Cycle)", styles["h1"]))
    story.append(
        Paragraph(
            "Calculated per Brihat Parashara Hora Shastra (BPHS) — the standard method used in "
            "the Government of India's official Panchang. Starting point is the balance of "
            "the Mahadasha lord at birth, determined by the Moon's position within the Janma Nakshatra.",
            styles["small"],
        )
    )
    story.append(Spacer(1, 0.15 * inch))

    dasha = chart.get("vimshottari_dasha", {})
    mahadashas = dasha.get("mahadashas", [])
    current_md = dasha.get("current_mahadasha")
    antardashas = dasha.get("antardashas", [])

    # Mahadasha table
    story.append(Paragraph("Mahadasha Sequence", styles["h2"]))
    rows = [["Mahadasha Lord", "Start Date", "End Date", "Duration (yrs)"]]
    for md in mahadashas:
        is_current = current_md and md["lord"] == current_md["lord"] and md["start"] == current_md["start"]
        lord_label = f"► {md['lord']}" if is_current else md["lord"]
        rows.append([
            lord_label,
            md["start"].strftime("%d %b %Y"),
            md["end"].strftime("%d %b %Y"),
            str(md["years"]),
        ])
    base_style = [
        ("BACKGROUND", (0, 0), (-1, 0), BRAND_GREEN),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.6),
        ("TEXTCOLOR", (0, 1), (-1, -1), INK),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#CDD6CE")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7FAF7")]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]
    for i, md in enumerate(mahadashas):
        if current_md and md["lord"] == current_md["lord"] and md["start"] == current_md["start"]:
            r = i + 1
            base_style += [
                ("BACKGROUND", (0, r), (-1, r), colors.HexColor("#E8F5E9")),
                ("FONTNAME", (0, r), (-1, r), "Helvetica-Bold"),
                ("TEXTCOLOR", (0, r), (-1, r), BRAND_GREEN),
            ]
    md_table = Table(rows, colWidths=[130, 100, 100, 100])
    md_table.setStyle(TableStyle(base_style))
    story.append(md_table)
    story.append(Spacer(1, 0.2 * inch))

    # Antardasha table for current mahadasha
    if current_md and antardashas:
        story.append(Paragraph(
            f"Antardasha within {current_md['lord']} Mahadasha "
            f"({current_md['start'].strftime('%d %b %Y')} – {current_md['end'].strftime('%d %b %Y')})",
            styles["h2"],
        ))
        today = date.today()
        ad_rows = [["Antardasha Lord", "Start Date", "End Date"]]
        for ad in antardashas:
            is_active = ad["start"] <= today < ad["end"]
            lord_label = f"► {ad['lord']}" if is_active else ad["lord"]
            ad_rows.append([lord_label, ad["start"].strftime("%d %b %Y"), ad["end"].strftime("%d %b %Y")])
        ad_table = Table(ad_rows, colWidths=[150, 120, 120])
        ad_style = [
            ("BACKGROUND", (0, 0), (-1, 0), SAFFRON),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 8.6),
            ("TEXTCOLOR", (0, 1), (-1, -1), INK),
            ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#CDD6CE")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#FFF8EE")]),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]
        for i, ad in enumerate(antardashas):
            if ad["start"] <= today < ad["end"]:
                r = i + 1
                ad_style += [
                    ("BACKGROUND", (0, r), (-1, r), colors.HexColor("#FFF0D0")),
                    ("FONTNAME", (0, r), (-1, r), "Helvetica-Bold"),
                ]
        ad_table.setStyle(TableStyle(ad_style))
        story.append(ad_table)
        story.append(Spacer(1, 0.1 * inch))
        story.append(Paragraph("► = currently active period", styles["small"]))

    # MD + AD combined effect box
    md_ad_effect = dasha.get("md_ad_effect", "")
    current_md = dasha.get("current_mahadasha")
    current_ad = dasha.get("current_antardasha")
    if md_ad_effect and current_md and current_ad:
        story.append(Spacer(1, 0.18 * inch))
        story.append(Paragraph(
            f"Combined Effect: {current_md['lord']} Mahadasha / {current_ad['lord']} Antardasha",
            styles["h2"],
        ))
        effect_table = Table([[Paragraph(md_ad_effect, styles["body"])]], colWidths=[430])
        effect_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F0F8F0")),
            ("BOX", (0, 0), (-1, -1), 0.75, BRAND_GREEN),
            ("LEFTPADDING", (0, 0), (-1, -1), 12),
            ("RIGHTPADDING", (0, 0), (-1, -1), 12),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ]))
        story.append(effect_table)
    story.append(Spacer(1, 0.15 * inch))


def _dosha_section(story: list, styles: dict, chart: dict) -> None:
    story.append(Paragraph("Dosha Analysis", styles["h1"]))
    story.append(
        Paragraph(
            "Doshas are karmic imprints identified in the natal chart. Their presence does not indicate misfortune — "
            "they indicate areas where the soul carries heightened karmic energy requiring conscious attention and specific remedial practice.",
            styles["small"],
        )
    )
    story.append(Spacer(1, 0.14 * inch))

    for dosha in chart.get("doshas", []):
        present = dosha["present"]
        status_color = SAFFRON if present else BRAND_GREEN
        status_text = f"{'PRESENT' if present else 'NOT PRESENT'} — {dosha['severity']}"

        # Header row with name + status
        header = Table(
            [[Paragraph(dosha["name"], styles["h2"]), Paragraph(status_text, styles["small"])]],
            colWidths=[280, 150],
        )
        header.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TEXTCOLOR", (1, 0), (1, 0), status_color),
            ("FONTNAME", (1, 0), (1, 0), "Helvetica-Bold"),
        ]))
        story.append(header)

        detail_para = Paragraph(f"<b>Position:</b> {dosha['detail']}", styles["body"])
        story.append(detail_para)
        story.append(Spacer(1, 0.05 * inch))

        if present and dosha.get("effect"):
            box_rows = []
            box_rows.append([
                Paragraph("<b>Effect:</b>", styles["body"]),
                Paragraph(dosha["effect"], styles["body"]),
            ])
            box_rows.append([
                Paragraph("<b>Remedy:</b>", styles["body"]),
                Paragraph(dosha["remedy"], styles["body"]),
            ])
            bg = colors.HexColor("#FFF8EE") if "Mangal" in dosha["name"] else colors.HexColor("#F5F0FF")
            border = SAFFRON if "Mangal" in dosha["name"] else colors.HexColor("#7B5EA7")
            box = Table(box_rows, colWidths=[70, 360])
            box.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), bg),
                ("BOX", (0, 0), (-1, -1), 0.75, border),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#E0D0C0")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]))
            story.append(box)

        story.append(Spacer(1, 0.2 * inch))


def _predictions(story: list, styles: dict, chart: dict) -> None:
    sections = chart.get("predictions", [])
    story.append(Paragraph("Basic Predictions", styles["h1"]))
    for heading, body in sections:
        story.append(Paragraph(heading, styles["h2"]))
        story.append(Paragraph(body, styles["body"]))
        story.append(Spacer(1, 0.14 * inch))


def _disclaimer(story: list, styles: dict) -> None:
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph("Important Note", styles["h2"]))
    story.append(
        Paragraph(
            "This report is intended for spiritual reflection and cultural guidance. The astronomical calculations "
            "use standard Nirayana Vedic conventions with Lahiri/Chitrapaksha ayanamsa, but the interpretations "
            "are not Government-certified predictions and should not replace medical, legal, financial, or other "
            "professional advice.",
            styles["small"],
        )
    )


def _info_table(rows: list[list[str]]) -> Table:
    table = Table(rows, colWidths=[145, 315])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), SOFT_GOLD),
                ("TEXTCOLOR", (0, 0), (0, -1), BRAND_GREEN),
                ("TEXTCOLOR", (1, 0), (1, -1), INK),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 9.5),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#D8C99D")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    return table


def _styles() -> dict:
    base = getSampleStyleSheet()
    return {
        "brand": ParagraphStyle(
            "Brand",
            parent=base["Title"],
            alignment=TA_CENTER,
            fontName="Helvetica-Bold",
            fontSize=26,
            leading=32,
            textColor=BRAND_GREEN,
        ),
        "cover_title": ParagraphStyle(
            "CoverTitle",
            parent=base["Title"],
            alignment=TA_CENTER,
            fontName="Helvetica-Bold",
            fontSize=21,
            leading=28,
            textColor=SAFFRON,
        ),
        "cover_name": ParagraphStyle(
            "CoverName",
            parent=base["Heading2"],
            alignment=TA_CENTER,
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=22,
            textColor=INK,
        ),
        "center_body": ParagraphStyle(
            "CenterBody",
            parent=base["BodyText"],
            alignment=TA_CENTER,
            fontName="Helvetica",
            fontSize=10.5,
            leading=16,
            textColor=MUTED,
        ),
        "h1": ParagraphStyle(
            "H1",
            parent=base["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=15,
            leading=19,
            spaceAfter=9,
            textColor=BRAND_GREEN,
        ),
        "h2": ParagraphStyle(
            "H2",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=11.2,
            leading=15,
            spaceBefore=3,
            spaceAfter=4,
            textColor=SAFFRON,
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["BodyText"],
            alignment=TA_LEFT,
            fontName="Helvetica",
            fontSize=10,
            leading=15,
            textColor=INK,
        ),
        "small": ParagraphStyle(
            "Small",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=8.8,
            leading=13,
            textColor=MUTED,
        ),
    }


def _footer(canvas, doc) -> None:
    canvas.saveState()
    width, _ = A4
    canvas.setStrokeColor(SAFFRON)
    canvas.setLineWidth(0.5)
    canvas.line(42, 32, width - 42, 32)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(42, 20, "Sattvic Gyaan - Basic Vedic Astrology Report")
    canvas.drawRightString(width - 42, 20, f"Page {doc.page}")
    canvas.restoreState()
