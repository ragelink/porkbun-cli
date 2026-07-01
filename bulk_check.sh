#!/bin/bash
# Bulk domain availability checker with rate limiting
set -euo pipefail

if [[ $# -eq 0 ]]; then
    echo "Usage: $0 domain1.com domain2.com ..." >&2
    exit 2
fi

# Credentials come from the environment (never hard-code secrets in source).
API_KEY="${PORKBUN_API_KEY:?set PORKBUN_API_KEY}"
SECRET_KEY="${PORKBUN_SECRET_KEY:?set PORKBUN_SECRET_KEY}"

available=()
taken=()
errors=()

first=1
for domain in "$@"; do
    # Validate the domain before using it in a URL (avoid injection / bad calls).
    if [[ ! "$domain" =~ ^[a-zA-Z0-9.-]+$ ]]; then
        echo "⚠️  $domain - invalid domain, skipping"
        errors+=("$domain")
        continue
    fi

    # Rate limit: 1 check per ~10s, but don't delay the very first check.
    if [[ $first -eq 0 ]]; then
        sleep 11
    fi
    first=0

    # Guard the request so a network/DNS/TLS failure doesn't abort the whole
    # loop under `set -e`; record it as an error and keep going.
    if ! result=$(curl -s -X POST "https://api-ipv4.porkbun.com/api/json/v3/domain/checkDomain/$domain" \
        -H "Content-Type: application/json" \
        -d "{\"apikey\":\"$API_KEY\",\"secretapikey\":\"$SECRET_KEY\"}"); then
        echo "⚠️  $domain - request failed"
        errors+=("$domain")
        continue
    fi

    if echo "$result" | grep -q '"avail":"yes"'; then
        price=$(echo "$result" | grep -o '"price":"[^"]*"' | cut -d'"' -f4)
        echo "✅ $domain - \$$price/yr"
        available+=("$domain:\$$price")
    elif echo "$result" | grep -q '"avail":"no"'; then
        echo "❌ $domain - taken"
        taken+=("$domain")
    else
        echo "⚠️  $domain - error: $result"
        errors+=("$domain")
    fi
done

echo ""
echo "=================================================="
echo "SUMMARY"
echo "=================================================="
echo ""
echo "✅ AVAILABLE (${#available[@]}):"
for d in "${available[@]}"; do
    echo "   $d"
done
echo ""
echo "❌ TAKEN (${#taken[@]}):"
for d in "${taken[@]}"; do
    echo "   $d"
done

if [[ ${#errors[@]} -gt 0 ]]; then
    echo ""
    echo "⚠️  ERRORS (${#errors[@]}):"
    for d in "${errors[@]}"; do
        echo "   $d"
    done
    exit 1
fi
