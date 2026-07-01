# OCR Provider Policy

Default provider: `mock_ocr`.

Supported providers:

- `mock_ocr`: local fixture provider, no network.
- `paddleocr_local`: optional local provider. Missing dependency returns `provider_unavailable`.
- `paddleocr_vl_local`: optional local/self-hosted provider. Missing model path returns `provider_unavailable`.
- `baidu_cloud_ocr`: optional cloud provider, disabled by default.
- `baidu_cloud_doc_parser`: optional cloud document parser, disabled by default.
- `external_json_import`: imports user-provided OCR JSON without provider calls.

Cloud OCR requires explicit `--allow-cloud-ocr` and safety evaluation. Sensitive input blocks cloud OCR.
