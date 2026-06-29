# route_har_miss_plus_network_404

## Primary Failure
- `playwright_route_mock_har` / `har_not_found_or_not_loaded`

## Secondary Failures
- `network_http_error` / `http_404`

## Blocking Failure
- route/HAR miss can leak to live network and produce HTTP errors

## Repair Order
- Fix route/HAR/mock registration before the first matching request.
- Then validate response shape and parser behavior.
