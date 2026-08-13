"""Tests for manuscript macro parsing and verification checks."""
from pathlib import Path

import pytest

from deceptive_email import verification as verif_mod


def test_parse_macros():
    text = r"""
    \newcommand{\RandomBestMacroFOne}{0.123}
    \newcommand{\SourceBestMacroFOne}{0.234}
    \newcommand{\NDocs}{10,000}
    """
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".tex", delete=False, encoding="utf-8") as fh:
        fh.write(text)
        p = Path(fh.name)
    try:
        macros = verif_mod.parse_macros(p)
    finally:
        p.unlink()
    assert macros["RandomBestMacroFOne"] == "0.123"
    assert macros["SourceBestMacroFOne"] == "0.234"
    assert macros["NDocs"] == "10,000"


def test_verify_manuscript_flags_placeholders(tmp_path):
    paper = tmp_path / "paper"
    (paper / "generated").mkdir(parents=True)
    (paper / "generated" / "result_macros.tex").write_text(
        r"\newcommand{\RandomBestMacroFOne}{0.000}" + "\n", encoding="utf-8")
    (paper / "manuscript.tex").write_text(
        "Some TBD placeholder text with a TODO and XX.\n", encoding="utf-8")
    report = verif_mod.verify_manuscript(paper, tmp_path)
    assert any("placeholder" in i for i in report["issues"])
    assert any("TODO" in i for i in report["issues"])


def test_verify_generated_numbers_catches_mismatch(tmp_path):
    run = tmp_path / "run"
    paper = tmp_path / "paper"
    (run / "metrics").mkdir(parents=True)
    (paper / "generated").mkdir(parents=True)
    import pandas as pd
    metrics = pd.DataFrame([
        {"split_id": "random_seed42", "protocol": "random", "model_id": "m1",
         "macro_f1": 0.90, "macro_f1_ci_low": 0.88, "macro_f1_ci_high": 0.92,
         "precision_pos": 0.9, "recall_pos": 0.9, "mcc": 0.8},
    ])
    metrics.to_csv(run / "metrics/all_metrics.csv", index=False)
    (paper / "generated" / "result_macros.tex").write_text(
        r"\newcommand{\RandomBestMacroFOne}{0.500}" + "\n", encoding="utf-8")
    (paper / "manuscript.tex").write_text("\\section{Results}\nWe report values.\n",
                                          encoding="utf-8")
    rep = verif_mod.verify_generated_numbers(run, paper)
    assert any("RandomBestMacroFOne" in i for i in rep["issues"])
