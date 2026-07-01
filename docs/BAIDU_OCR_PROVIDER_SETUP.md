# Baidu OCR Provider Setup

Baidu cloud OCR providers are optional and disabled by default.

They require:

```powershell
$env:BAIDU_OCR_API_KEY = "..."
$env:BAIDU_OCR_SECRET = "..."
failure-doctor ocr-evidence extract --input .\safe_redacted_document --out .\ocr_report --provider baidu_cloud_doc_parser --allow-cloud-ocr --safety-evaluate
```

The public package does not upload by default. If sensitive text, customer data, tokens, cookies, authorization headers, order data, or personal data are detected, the provider is blocked.
