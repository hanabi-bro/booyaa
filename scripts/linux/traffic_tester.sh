#!/usr/bin/env bash
set -euo pipefail

PYTHON="$HOME/.local/booyaa/.venv/bin/python"

usage() {
    cat <<'EOF'
Usage:
    traffic_tester <mode> [args...]

Modes:
    http-server
    http-client
    https-server
    https-client
    tcp-server
    tcp-client
    udp-server
    udp-client

Example:
    traffic_tester http-server 80
    traffic_tester http-client 127.0.0.1 80 --duration 60
EOF
}

if [[ $# -lt 1 ]]; then
    usage
    exit 1
fi

mode="$1"
shift

case "$mode" in
    http-server)  module="booyaa.traffic_tester.http.server" ;;
    http-client)  module="booyaa.traffic_tester.http.client" ;;
    https-server) module="booyaa.traffic_tester.https.server" ;;
    https-client) module="booyaa.traffic_tester.https.client" ;;
    tcp-server)   module="booyaa.traffic_tester.tcp.server" ;;
    tcp-client)   module="booyaa.traffic_tester.tcp.client" ;;
    udp-server)   module="booyaa.traffic_tester.udp.server" ;;
    udp-client)   module="booyaa.traffic_tester.udp.client" ;;
    -h|--help|help)
        usage
        exit 0
        ;;
    *)
        echo "Unknown mode: $mode" >&2
        echo >&2
        usage >&2
        exit 2
        ;;
esac

exec "$PYTHON" -m "$module" "$@"
