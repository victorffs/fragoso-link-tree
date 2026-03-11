#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${DEPLOY_BASE_URL:-https://frago.so}"

echo "[1/3] Running local contract tests..."
python -m unittest discover -s tests -v

echo "[2/3] Running live post-deploy smoke test on ${BASE_URL}..."
RUN_DEPLOY_SMOKE=1 DEPLOY_BASE_URL="${BASE_URL}" python -m unittest tests/test_post_deploy_smoke.py -v

echo "[3/3] Verifying critical CSS classes on live CSS..."
css_url="${BASE_URL%/}/styles/main.css?smoke_ts=$(date +%s%N)"
css_content="$(curl -s -H "Cache-Control: no-cache" -H "Pragma: no-cache" "${css_url}")"

for selector in ".quick-grid" ".quick-card" ".share-cta" ".share-feedback"; do
	echo "${css_content}" | grep -Fq "${selector}"
done

echo "✅ Post-deploy checks passed for ${BASE_URL}"
