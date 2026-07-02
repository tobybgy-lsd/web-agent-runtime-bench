# Anonymization Policy

The v4.3 case intake pipeline redacts common secrets, bearer tokens, cookies,
password fields, local user paths, emails, and payment-like digit sequences from
text evidence before creating a public case.

The anonymizer is a safety layer, not permission to publish raw materials.
Maintainers must still run publish-check and review the generated case.
