# Exact Tightness on the Second Subset Diagonal of the Avoid-or-Compress Lemma

Ryutaro Yonezu — Independent Researcher

This repository contains the paper source, compiled PDF, and an independent verifier for the second subset diagonal of the avoid-or-compress lemma.

## Main result

Let `A ⊂ S ⊆ Q` with `|S|-|A|=2` in a synchronizing DFA with `n=|Q|`.

- If `S=Q`, the exact worst-case avoid-or-compress distance is `1`.
- If `S⊊Q`, the exact worst-case distance is

  `n-|A| = n-|S|+2`.

The proper-subset lower bound is attained by explicit binary, strongly connected, synchronizing automata.

## Files

- `Yonezu_2026_No17_Second_Diagonal.pdf` — compiled paper.
- `Yonezu_2026_No17_Second_Diagonal.tex` — LaTeX source.
- `NO17_SECOND_DIAGONAL_VERIFY.py` — independent verifier.
- `VERIFICATION_OUTPUT.txt` — output from the default audit run.
- `SHA256SUMS.txt` — SHA-256 manifest for the release files.
- `CITATION.cff` — citation metadata. A DOI can be added after archival publication.

## Reproduce the computational audit

Requirements: Python 3.9+; no external packages.

```bash
python NO17_SECOND_DIAGONAL_VERIFY.py
```

Expected summary:

```json
{
  "r_range": [1, 30],
  "L_range": [3, 40],
  "cases": 1140,
  "failures": 0,
  "all_pass": true,
  "max_n": 70
}
```

The verifier independently checks, for every tested parameter pair:

1. the exact first successful avoid-or-compress distance equals `L=n-|A|`;
2. the closed-form length-`L` witness succeeds;
3. strong connectivity;
4. entry into the synchronization core;
5. an explicit reset word maps the full state set to a singleton.

To export all per-instance results:

```bash
python NO17_SECOND_DIAGONAL_VERIFY.py --json audit_full.json
```

## Scope of the computation

The default grid is

- `1 ≤ |A| = r ≤ 30`,
- `3 ≤ L = n-|A| ≤ 40`,
- 1,140 constructions total,
- up to `n=70`.

The computation is reproducibility support; the exact theorem is proved analytically in the paper.

## Version

Prepared for `v1.0.0`, 22 September 2026.
