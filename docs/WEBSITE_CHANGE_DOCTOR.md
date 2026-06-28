# Website Change Doctor

Website Change diagnosis separates automation-code mistakes from target-site contract changes.

## Failure Layer

`failure_layer: website_change`

## Subtypes

- `selector_drift`
- `dom_structure_changed`
- `api_endpoint_changed`
- `response_shape_changed`
- `graphql_schema_changed`
- `pagination_changed`
- `login_flow_changed`
- `download_behavior_changed`

## Evidence

- old selector no longer resolves, but a similar DOM candidate exists
- DOM path or component hierarchy changed
- endpoint returns 404, 410, 301, or redirects to a new route
- JSON key is missing or renamed
- GraphQL reports `Cannot query field`
- next cursor or pagination token changed
- login flow gained MFA, consent, or a new intermediate page
- direct download changed into an async export job

## Safe Repair Direction

- capture a fresh sanitized trace, DOM snapshot, and network.json
- update selectors, endpoint routes, JSON paths, pagination, login flow, or download flow
- ask Codex to edit the automation script from the new evidence
- add a regression test for the new site contract

Website Change Doctor should not produce access-control defeat guidance. If evidence points to a risk or challenge layer, classify as `anti_bot_risk` or `insufficient_evidence`.
