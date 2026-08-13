# Visual layout check

- PDF: `paper/build/manuscript.pdf`
- Pages: 8 (confirmed from `paper/build/manuscript.log` line 372: `Output written on ... manuscript.pdf (8 pages, 219682 bytes)`)
- Build log warnings: only `Underfull \hbox` (lines 280, 330) and `Underfull \vbox` (line 326). No `Overfull \hbox`, no undefined references, no unresolved citations.
- Tables (per `paper/build/manuscript.aux`): 7 tables total (I-VII):
  - Table I: dataset_table (3 cols × 4 rows: source, benign, positive, total).
  - Table II: holdout_table (6 rows × 6 cols: held-out sources × M1..A2).
  - Table III: cluster_leakage (6 rows × 5 cols).
  - Table IV: performance_table (66 rows: 36 SD + 6 Rand + 6 Sec + 18 RCD-p).
  - Table V: per_model_gap (6 rows × 6 cols).
  - Table VI: decomposition (6 rows × 5 cols).
  - Table VII: paired_delta (12 rows × 6 cols, including Cohen's $d$ column with full values like 1.69).

**Status: verified clean for issues #2 and #3.** No truncation observed. Cohen's $d$ column at Table VII shows full values. Tables do not overlap. No continuation notice needed.