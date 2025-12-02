#!/bin/sh

HTML_FILE=/home/adminuser/venv/site-packages/streamlit/static/index.html
INJECT_FILE=/mount/src/nba-agent/injected-script.html

if [ ! -f "$HTML_FILE" ]; then
  echo "Error: HTML file '$HTML_FILE' not found."
  exit 1
fi

if [ ! -f "$INJECT_FILE" ]; then
  echo "Error: Injection file '$INJECT_FILE' not found."
  exit 1
fi

INJECTION=$(<"$INJECT_FILE")
awk -v injection="$INJECTION" '
    BEGIN { IGNORECASE = 1 }
    /<head[^>]*>/ {
        print
        print injection
        next
    }
    { print }
' "$HTML_FILE" > "${HTML_FILE}.tmp" && mv "${HTML_FILE}.tmp" "$HTML_FILE"
