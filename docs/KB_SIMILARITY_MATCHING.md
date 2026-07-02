# KB Similarity Matching

The v3.9 KB uses local explainable matching only. It does not call external
embedding APIs.

Signals:

- failure type
- subtype
- framework
- domain
- evidence fingerprint
- normalized error tokens
- network, DOM, visual, OCR, data-quality, safety, and regulated signatures

Output includes a score, matched dimensions, why it matched, and why it is not
an exact proof. Similar cases must be verified before reuse.
