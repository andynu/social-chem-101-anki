#!/usr/bin/env python3
"""Build an Anki deck from the Social-Chem-101 dataset."""

import html
import hashlib

import genanki
import pandas as pd

TSV_PATH = "social-chem-101/social-chem-101.v1.0.tsv"
OUTPUT_PATH = "social-chem-101.apkg"

# Stable IDs derived from the deck name
DECK_ID = int(hashlib.md5(b"Social-Chem-101").hexdigest()[:8], 16)
MODEL_ID = int(hashlib.md5(b"Social-Chem-101-Model").hexdigest()[:8], 16)

CARD_CSS = """\
.card {
  font-family: "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  font-size: 18px;
  text-align: center;
  color: #1a1a2e;
  background: #f5f5f5;
  padding: 20px;
  line-height: 1.5;
}
.rot {
  font-size: 22px;
  font-style: italic;
  color: #16213e;
  margin: 20px 0;
  padding: 20px;
  background: #fff;
  border-left: 4px solid #0f3460;
  border-radius: 4px;
  text-align: left;
}
.back-section {
  text-align: left;
  max-width: 500px;
  margin: 0 auto;
}
.label {
  font-weight: bold;
  color: #0f3460;
  margin-top: 14px;
  margin-bottom: 2px;
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.value {
  margin: 0 0 8px 0;
  padding: 6px 10px;
  background: #fff;
  border-radius: 4px;
}
.moral-scale {
  font-size: 20px;
  letter-spacing: 4px;
  padding: 8px 10px;
  background: #fff;
  border-radius: 4px;
}
.category-tags {
  margin-top: 14px;
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.cat-tag {
  display: inline-block;
  background: #e2e8f0;
  color: #334155;
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 12px;
}
"""

FRONT_TEMPLATE = """\
<div class="rot">{{RoT}}</div>
<p style="color:#888; font-size:14px;">What is the situation, action, and moral judgment?</p>
"""

BACK_TEMPLATE = """\
<div class="rot">{{RoT}}</div>
<hr>
<div class="back-section">
  <div class="label">Situation</div>
  <div class="value">{{Situation}}</div>

  <div class="label">Action</div>
  <div class="value">{{Action}}</div>

  <div class="label">Judgment</div>
  <div class="value">{{Judgment}}</div>

  <div class="label">Moral Score</div>
  <div class="moral-scale">{{MoralScale}}</div>

  <div class="label">Legality</div>
  <div class="value">{{Legality}}</div>

  <div class="label">Category</div>
  <div class="category-tags">{{Category}}</div>
</div>
"""

model = genanki.Model(
    MODEL_ID,
    "Social-Chem-101",
    fields=[
        {"name": "RoT"},
        {"name": "Situation"},
        {"name": "Action"},
        {"name": "Judgment"},
        {"name": "MoralScale"},
        {"name": "Legality"},
        {"name": "Category"},
    ],
    templates=[
        {
            "name": "RoT → Details",
            "qfmt": FRONT_TEMPLATE,
            "afmt": BACK_TEMPLATE,
        },
    ],
    css=CARD_CSS,
)


def moral_score_visual(score: float) -> str:
    """Convert -2..+2 score to a visual dot scale."""
    if pd.isna(score):
        score = 0
    score = int(score)
    labels = {-2: "Very Bad", -1: "Bad", 0: "Neutral", 1: "Good", 2: "Very Good"}
    dots = []
    for i in range(-2, 3):
        if i == score:
            dots.append("&#9679;")  # filled circle
        else:
            dots.append("&#9675;")  # empty circle
    label = labels.get(score, "")
    return " ".join(dots) + f"&nbsp; {label}"


def category_html(cat_str: str) -> str:
    """Convert pipe-separated categories to styled tags."""
    if pd.isna(cat_str):
        return '<span class="cat-tag">unknown</span>'
    return " ".join(
        f'<span class="cat-tag">{html.escape(c)}</span>'
        for c in cat_str.split("|")
    )


def moral_foundation_tags(mf_str: str) -> list[str]:
    """Convert moral foundations string to Anki tags."""
    if pd.isna(mf_str):
        return []
    return [f"moral::{f.strip()}" for f in mf_str.split("|")]


def stable_note_id(rot_id: str) -> int:
    """Generate a stable GUID-compatible integer from the rot-id."""
    return int(hashlib.md5(rot_id.encode()).hexdigest()[:12], 16)


def main():
    print("Loading dataset...")
    df = pd.read_csv(TSV_PATH, sep="\t")
    print(f"  Total rows: {len(df):,}")

    # Filter
    mask = (
        (df["rot-bad"] == 0)
        & (df["rot-agree"] >= 3)
        & (df["split"].isin(["train", "dev", "test"]))
        & df["action"].notna()
        & df["rot-judgment"].notna()
    )
    df = df[mask].copy()
    print(f"  After quality filter: {len(df):,}")

    # Deduplicate: one RoT per situation, keep highest agreement
    df = df.sort_values("rot-agree", ascending=False)
    df = df.drop_duplicates(subset=["situation-short-id"], keep="first")
    print(f"  After dedup (one per situation): {len(df):,}")

    # Build deck
    deck = genanki.Deck(DECK_ID, "Social-Chem-101")

    def safe_str(val: object) -> str:
        if pd.isna(val):
            return ""
        return str(val)

    for _, row in df.iterrows():
        fields = [
            html.escape(safe_str(row["rot"])),
            html.escape(safe_str(row["situation"])),
            html.escape(safe_str(row["action"])),
            html.escape(safe_str(row["rot-judgment"])),
            moral_score_visual(row["action-moral-judgment"]),
            html.escape(safe_str(row["action-legal"])),
            category_html(row["rot-categorization"]),
        ]
        tags = moral_foundation_tags(row["rot-moral-foundations"])

        note = genanki.Note(
            model=model,
            fields=fields,
            tags=tags,
            guid=stable_note_id(str(row["rot-id"])),
        )
        deck.add_note(note)

    print(f"  Notes created: {len(deck.notes):,}")

    # Write .apkg
    genanki.Package(deck).write_to_file(OUTPUT_PATH)
    print(f"  Written to {OUTPUT_PATH}")

    # File size
    import os

    size_mb = os.path.getsize(OUTPUT_PATH) / (1024 * 1024)
    print(f"  File size: {size_mb:.1f} MB")


if __name__ == "__main__":
    main()
