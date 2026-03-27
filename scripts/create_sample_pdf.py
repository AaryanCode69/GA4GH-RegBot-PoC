from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from fpdf import FPDF

from config import SAMPLE_PDF_PATH

POLICY_TITLE: str = (
    "GA4GH Framework for Responsible Sharing of Genomic and Health-Related Data"
)
POLICY_SUBTITLE: str = "Version 1.0  |  Sample PoC Reference Document"
ATTRIBUTION_FOOTER: str = (
    "Created by GA4GH  |  Use and reproduction subject to the GA4GH Copyright Policy"
    "  |  https://www.ga4gh.org/copyright-policy/"
)

# ─────────────────────────────────────────────────────────────────────────────
# Policy content
# Each entry is a (text, is_heading) tuple.
# Headings are rendered bold/blue; body paragraphs are rendered in normal weight.
# ─────────────────────────────────────────────────────────────────────────────

PAGE_1_SECTIONS: list[tuple[str, bool]] = [
    # ── Section 1 ────────────────────────────────────────────────────────────
    (
        "1. Principle of Respect for Persons and Populations",
        True,
    ),
    (
        "All individuals and groups who contribute their genomic and health-related "
        "data must be treated with respect, dignity, and fairness. Data sharing "
        "activities must uphold the autonomy of data contributors and must not "
        "discriminate against any individual or group on the basis of genomic "
        "characteristics, ancestry, or health status.",
        False,
    ),
    # ── Section 2 ────────────────────────────────────────────────────────────
    (
        "2. Principle of Benefit Sharing",
        True,
    ),
    (
        "The benefits derived from genomic data sharing should be distributed "
        "equitably among all contributing populations. Institutions that access "
        "shared data for research purposes are expected to make reasonable efforts "
        "to ensure that research outcomes and derived benefits are accessible to "
        "the communities from which data originated, including communities in "
        "low- and middle-income countries.",
        False,
    ),
    # ── Section 3 ────────────────────────────────────────────────────────────
    (
        "3. Consent and Data Use Limitations",
        True,
    ),
    (
        "Data contributors must provide free, prior, and informed consent before "
        "their genomic or health-related data is collected or shared. Consent must "
        "specify the permitted scope of data use, including any restrictions on "
        "secondary use, commercial research, or sharing with third parties. Any use "
        "of shared data that exceeds the scope defined in the original consent "
        "agreement is strictly prohibited and must be reported to the responsible "
        "Data Access Committee without delay.",
        False,
    ),
    # ── Section 4 ────────────────────────────────────────────────────────────
    (
        "4. Data Access and Governance",
        True,
    ),
    (
        "Access to controlled-access genomic datasets must be governed by a Data "
        "Access Committee (DAC) or equivalent oversight body. Requests to access "
        "controlled data must be reviewed against the original consent terms, the "
        "stated research purpose, and the applicable data use limitations encoded in "
        "the Data Use Ontology (DUO). Access approvals must be time-limited, "
        "documented in an auditable access log, and subject to periodic review no "
        "less than once per calendar year.",
        False,
    ),
]

PAGE_2_SECTIONS: list[tuple[str, bool]] = [
    # ── Section 5 ────────────────────────────────────────────────────────────
    (
        "5. Privacy and Security Obligations",
        True,
    ),
    (
        "All organisations handling shared genomic data must implement technical "
        "and organisational safeguards proportionate to the sensitivity of the data. "
        "At minimum, this includes encryption of data in transit and at rest, strict "
        "role-based access controls, audit logging of all data access events, and a "
        "documented incident response procedure. No genomic data may be stored in "
        "environments that do not meet these minimum security requirements.",
        False,
    ),
    # ── Section 6 ────────────────────────────────────────────────────────────
    (
        "6. Accountability and Transparency",
        True,
    ),
    (
        "Institutions and researchers who access shared data are accountable for "
        "compliance with the terms of the data access agreement and the original "
        "consent conditions. Any breach of data use conditions must be reported to "
        "the responsible DAC within 72 hours of discovery. Repeated or wilful "
        "violations of data use conditions may result in permanent revocation of "
        "data access privileges and referral to the relevant institutional "
        "review authority.",
        False,
    ),
    # ── Section 7 ────────────────────────────────────────────────────────────
    (
        "7. Cross-Jurisdictional Compliance",
        True,
    ),
    (
        "Where genomic data sharing involves organisations or data subjects located "
        "in multiple legal jurisdictions, all parties must identify and comply with "
        "the applicable legal frameworks in each jurisdiction. Where legal "
        "requirements conflict, the more protective standard shall apply. "
        "Institutions must document their cross-jurisdictional compliance assessment "
        "prior to initiating any international data sharing activity and must retain "
        "that documentation for a minimum of five years.",
        False,
    ),
    # ── Section 8 ────────────────────────────────────────────────────────────
    (
        "8. Review and Revision",
        True,
    ),
    (
        "This policy framework shall be reviewed no less than once every three "
        "years, or sooner if significant legislative, technological, or ethical "
        "developments warrant earlier revision. Proposed amendments must be "
        "subject to public consultation for a period of not less than sixty days "
        "before adoption. The effective date of any revision and a summary of "
        "material changes shall be clearly stated in the updated document and "
        "communicated to all registered data access applicants.",
        False,
    ),
]


# ─────────────────────────────────────────────────────────────────────────────
# PDF class
# ─────────────────────────────────────────────────────────────────────────────


class PolicyPDF(FPDF):
    """Custom FPDF subclass with policy-document header and footer."""

    def header(self) -> None:
        # Title line
        self.set_font("Helvetica", style="B", size=10)
        self.set_text_color(30, 60, 120)
        self.cell(
            0,
            8,
            POLICY_TITLE,
            align="C",
            new_x="LMARGIN",
            new_y="NEXT",
        )
        # Subtitle / version line
        self.set_font("Helvetica", style="", size=8)
        self.set_text_color(100, 100, 100)
        self.cell(
            0,
            5,
            POLICY_SUBTITLE,
            align="C",
            new_x="LMARGIN",
            new_y="NEXT",
        )
        # Horizontal rule
        self.ln(2)
        self.set_draw_color(180, 180, 180)
        self.line(self.l_margin, self.get_y(), 210 - self.r_margin, self.get_y())
        self.ln(5)

    def footer(self) -> None:
        self.set_y(-14)
        self.set_font("Helvetica", style="I", size=7)
        self.set_text_color(140, 140, 140)
        # Attribution notice (left) + page number (right)
        self.cell(
            0,
            8,
            ATTRIBUTION_FOOTER,
            align="L",
            new_x="LMARGIN",
            new_y="NEXT",
        )
        self.set_y(-9)
        self.cell(0, 6, f"Page {self.page_no()}", align="R")


# ─────────────────────────────────────────────────────────────────────────────
# Rendering helpers
# ─────────────────────────────────────────────────────────────────────────────


def _render_sections(pdf: PolicyPDF, sections: list[tuple[str, bool]]) -> None:
    """Write a list of (text, is_heading) section tuples to the current page."""
    for text, is_heading in sections:
        if is_heading:
            pdf.ln(5)
            pdf.set_font("Helvetica", style="B", size=11)
            pdf.set_text_color(20, 55, 115)
            pdf.multi_cell(0, 7, text, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(1)
        else:
            pdf.set_font("Helvetica", style="", size=10)
            pdf.set_text_color(30, 30, 30)
            pdf.multi_cell(0, 6, text, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(2)


# ─────────────────────────────────────────────────────────────────────────────
# Public build function
# ─────────────────────────────────────────────────────────────────────────────


def build_pdf(output_path: Path) -> None:
    """
    Generate the sample GA4GH policy PDF and write it to *output_path*.

    Parameters
    ----------
    output_path : Path
        Destination file path. Parent directory is created automatically.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    pdf = PolicyPDF()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.set_margins(left=18, top=22, right=18)

    # ── Page 1: Sections 1–4 ─────────────────────────────────────────────────
    pdf.add_page()
    _render_sections(pdf, PAGE_1_SECTIONS)

    # ── Page 2: Sections 5–8 ─────────────────────────────────────────────────
    pdf.add_page()
    _render_sections(pdf, PAGE_2_SECTIONS)

    pdf.output(str(output_path))

    total_sections = sum(1 for _, is_h in PAGE_1_SECTIONS if is_h) + sum(
        1 for _, is_h in PAGE_2_SECTIONS if is_h
    )
    print(f"[create_sample_pdf] ✓ PDF written  : {output_path}")
    print(f"[create_sample_pdf]   Pages         : 2")
    print(f"[create_sample_pdf]   Sections      : {total_sections}")
    print(
        f"[create_sample_pdf]   Body paragraphs: "
        f"{len(PAGE_1_SECTIONS) + len(PAGE_2_SECTIONS) - total_sections}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    build_pdf(SAMPLE_PDF_PATH)
