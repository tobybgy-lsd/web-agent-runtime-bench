# Static Product List Example

**Type**: Synthetic HTML + expected extraction schema
**Synthetic Only**: Yes. All URLs use local `/demo/products/` paths.

## Files

- `sample_input.html` — Synthetic product list with 3 items
- `expected_schema.json` — Field definitions (title, price, stock, rating, product_url)
- `expected_output.json` — Expected extraction result

## Usage

This example illustrates web data extraction without needing a live website:

```powershell
# Inspect the sample
cat sample_input.html

# Review expected schema
cat expected_schema.json

# Review expected output
cat expected_output.json
```

No external network needed. All product URLs are local `/demo/products/` paths.
