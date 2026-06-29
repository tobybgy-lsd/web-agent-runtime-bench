# Composite Diagnosis

Composite diagnosis upgrades Agent Failure Doctor from a single best failure type
to a deterministic evidence model:

```text
failure artifact
-> evidence nodes
-> diagnosis candidates
-> evidence graph
-> primary / secondary / blocking / downstream failures
-> repair order
```

## Concepts

- Primary failure: the most likely root or blocking cause to fix first.
- Secondary failure: another detected failure that may remain after the primary is fixed.
- Blocking failure: the failure that prevents downstream evidence from being trusted.
- Downstream failure: a symptom caused by the primary or blocking failure.
- Competing hypothesis: a plausible diagnosis that does not have enough causal support to become primary.

## Evidence Graph

The graph stores compact local evidence nodes and causal edges such as `blocks`,
`likely_causes`, and `competes_with`. It intentionally keeps excerpts short and
does not copy raw traces, cookies, tokens, or authorization headers.

## Repair Order

Repair order follows causal priority:

1. Access-control boundary, network, runtime, or auth blockers first.
2. Route/HAR/mock issues before response parsing.
3. Frame, popup, shadow DOM, or page targeting before selector changes.
4. Selectors, schema, and business mappings after blockers are resolved.

## Safety Boundary

Anti-bot and access-risk cases are diagnosis and compliance-routing cases only.
The tool does not provide CAPTCHA bypass, bot evasion, fingerprint spoofing,
dynamic signature cracking, IP/account pool guidance, ban evasion, or
unauthorized scraping advice.

## Limits

P95 means the strict local validation gate passes for modeled automation failure
families. It does not mean the tool can infer arbitrary unknown business logic
without structured evidence.
