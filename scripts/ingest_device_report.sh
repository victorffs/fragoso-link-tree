#!/usr/bin/env bash
set -euo pipefail

BASE_URL="https://frago.so"
TITLE=""
DEVICE=""
SCREENSHOT=""
REPORTER=""
NOTES=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --title)
      TITLE="$2"
      shift 2
      ;;
    --device)
      DEVICE="$2"
      shift 2
      ;;
    --url)
      BASE_URL="$2"
      shift 2
      ;;
    --screenshot)
      SCREENSHOT="$2"
      shift 2
      ;;
    --reporter)
      REPORTER="$2"
      shift 2
      ;;
    --notes)
      NOTES="$2"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1"
      exit 1
      ;;
  esac
done

if [[ -z "$TITLE" || -z "$DEVICE" ]]; then
  echo "Usage: bash scripts/ingest_device_report.sh --title \"...\" --device \"...\" [--url https://frago.so] [--screenshot /path/image.png] [--reporter name] [--notes \"...\"]"
  exit 1
fi

slug="$(echo "$TITLE" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g; s/^-+|-+$//g')"
timestamp="$(date +%Y%m%d-%H%M%S)"
incident_dir="reports/incidents/${timestamp}-${slug}"

mkdir -p "$incident_dir"

html_url="${BASE_URL%/}/"
css_url="${BASE_URL%/}/styles/main.css"

curl -s -H "Cache-Control: no-cache" -H "Pragma: no-cache" "${html_url}?ingest_ts=$(date +%s%N)" > "$incident_dir/live_homepage.html"
curl -s -H "Cache-Control: no-cache" -H "Pragma: no-cache" "${css_url}?ingest_ts=$(date +%s%N)" > "$incident_dir/live_main.css"

if [[ -n "$SCREENSHOT" && -f "$SCREENSHOT" ]]; then
  ext="${SCREENSHOT##*.}"
  if [[ "$ext" == "$SCREENSHOT" ]]; then
    ext="png"
  fi
  screenshot_name="screenshot.${ext}"
  cp "$SCREENSHOT" "$incident_dir/$screenshot_name"
  screenshot_ref="$(basename "$incident_dir")/$screenshot_name"
else
  screenshot_ref="(not provided)"
fi

{
  echo "# Incident Report"
  echo
  echo "- Title: $TITLE"
  echo "- Timestamp: $timestamp"
  echo "- Reporter: ${REPORTER:-unknown}"
  echo "- Device: $DEVICE"
  echo "- URL: $BASE_URL"
  echo "- Screenshot: $screenshot_ref"
  echo
  echo "## Notes"
  echo "${NOTES:-No notes provided.}"
  echo
  echo "## Reproduction checklist"
  echo "1. Open $BASE_URL on device: $DEVICE"
  echo "2. Hard refresh"
  echo "3. Compare layout with expected quick cards"
  echo
  echo "## Evidence files"
  echo "- live_homepage.html"
  echo "- live_main.css"
  echo
  echo "## Automated checks"
  echo "Run: DEPLOY_BASE_URL=$BASE_URL bash scripts/post_deploy_check.sh"
} > "$incident_dir/report.md"

if DEPLOY_BASE_URL="$BASE_URL" bash scripts/post_deploy_check.sh > "$incident_dir/post_deploy_check.log" 2>&1; then
  status="PASS"
else
  status="FAIL"
fi

echo "Automated check status: $status" >> "$incident_dir/report.md"

echo "Created incident bundle: $incident_dir"
echo "Check status: $status"
