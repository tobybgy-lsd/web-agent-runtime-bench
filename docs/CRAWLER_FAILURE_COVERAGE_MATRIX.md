# Crawler Failure Coverage Matrix

This matrix turns crawler and browser automation coverage into a measurable P98 gate.

It covers:

1. static_html_extraction
2. dynamic_rendering
3. ajax_xhr
4. graphql_api
5. websocket_sse
6. pagination
7. infinite_scroll
8. virtualized_list
9. lazy_loading
10. login_session
11. cookie_storage_state
12. file_download
13. file_upload
14. network_proxy_dns_tls
15. framework_runtime
16. data_schema
17. business_mapping
18. anti_bot_risk_boundary
19. cross_framework
20. composite_failures

Generate the machine-readable matrix:

```powershell
python -m tools.validation.run_crawler_failure_coverage_matrix
```

P98 requires at least 20 categories, at least 200 mapped cases, zero forbidden output, and an explicit gap backlog.

