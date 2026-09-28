"""Mechanically rename human-facing LSTM variants; preserve experiment keys."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FILES = [
    "Finals_Revised_Paper_WASD.md", "CHAPTER_IV_RESULTS_AND_DISCUSSION.md",
    "CHAPTER_V_SUMMARY_CONCLUSIONS_AND_RECOMMENDATIONS.md",
    "PANEL_COMMENTS_MATRIX.md", "PRESENTATION_SPEAKER_SCRIPT.md",
    "ABSTRACT_F2.md", "F1_THRESHOLD_VALIDATION_ANALYSIS.md",
]
REPLACEMENTS = [
    ("primary matched seven-feature LSTM", "Trajectory-Feature LSTM"),
    ("Primary trajectory LSTM", "Trajectory-Feature LSTM"),
    ("primary seven-feature LSTM", "Trajectory-Feature LSTM"),
    ("Primary seven-feature LSTM", "Trajectory-Feature LSTM"),
    ("primary matched-input LSTM", "Trajectory-Feature LSTM"),
    ("Secondary enhanced-input LSTM only", "Embedding-and-Feature LSTM"),
    ("secondary enhanced-input LSTM", "Embedding-and-Feature LSTM"),
    ("Enhanced-input LSTM", "Embedding-and-Feature LSTM"),
    ("enhanced-input LSTM", "Embedding-and-Feature LSTM"),
    ("primary and enhanced LSTMs", "Trajectory-Feature and Embedding-and-Feature LSTMs"),
    ("primary or enhanced LSTM", "Trajectory-Feature or Embedding-and-Feature LSTM"),
    ("selected primary model", "selected Trajectory-Feature LSTM"),
    ("selected enhanced model", "selected Embedding-and-Feature LSTM"),
    ("primary Layer 2 model", "seven-feature Layer 2 model"),
    ("primary-LSTM", "Trajectory-Feature LSTM"),
    ("Primary LSTM", "Trajectory-Feature LSTM"),
    ("primary LSTM", "Trajectory-Feature LSTM"),
    ("Enhanced LSTM", "Embedding-and-Feature LSTM"),
    ("enhanced LSTM", "Embedding-and-Feature LSTM"),
    ("Primary, seven features", "Trajectory-Feature LSTM"),
    ("Enhanced, features + embeddings", "Embedding-and-Feature LSTM"),
    ("Primary, equal-length mix", "Trajectory-Feature LSTM, equal-length mix"),
    ("Enhanced, equal-length mix", "Embedding-and-Feature LSTM, equal-length mix"),
    ("primary recurrent classifier", "trajectory-feature recurrent classifier"),
    ("enhanced recurrent model", "embedding-and-feature recurrent model"),
    ("enhanced classifier", "embedding-and-feature classifier"),
    ("primary model", "trajectory-feature model"),
    ("enhanced model", "embedding-and-feature model"),
    ("primary variant", "trajectory-feature variant"),
    ("enhanced variant", "embedding-and-feature variant"),
    ("enhanced representation", "embedding-and-feature representation"),
    ("Primary precision", "Trajectory-model precision"),
    ("Primary pooled values:", "Trajectory-Feature LSTM pooled values:"),
    ("; enhanced:", "; Embedding-and-Feature LSTM:"),
    ("while enhanced has", "while the Embedding-and-Feature LSTM has"),
    ("Enhanced had", "The Embedding-and-Feature LSTM had"),
]

for name in FILES:
    path = ROOT / "thesis_docs" / name
    original = path.read_text(encoding="utf-8")
    revised = original
    for old, new in REPLACEMENTS:
        revised = revised.replace(old, new)
    if revised != original:
        path.write_text(revised, encoding="utf-8")
        print(name)
