# Spiderbuf-Inspired Challenge Validation Pack

This pack is inspired by public crawler training challenge categories from `hhuayuan/spiderbuf`.

It is local-only, mock-based, and diagnosis-only. It does not access spiderbuf.cn, does not include private solutions, and does not include instructions for defeating access controls. The goal is to validate Agent Failure Doctor on realistic failure shapes while keeping public artifacts safe and reproducible.

## Cases

1. cookie required
2. iframe extraction
3. ajax dynamic loading
4. random CSS class selector drift
5. infinite scroll missing items
6. rate limit 429
7. API signature required
8. browser fingerprint risk
9. Selenium detection risk
10. challenge page detected

Reproduce:

```powershell
python -m tools.validation.run_spiderbuf_inspired_validation
```
