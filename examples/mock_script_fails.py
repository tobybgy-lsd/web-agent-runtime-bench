import sys


print("mock browser automation started")
print("page.goto: net::ERR_PROXY_CONNECTION_FAILED while opening https://example.test", file=sys.stderr)
sys.exit(7)
