# fragoso-link-tree
My own link tree

## Deploy (Netlify)

This is a static site. Netlify should publish the repository root (`.`).

- Build command: *(empty)*
- Publish directory: `.`
- Config file: `netlify.toml`

## Post-deploy smoke test

Run this after each production deploy to validate key links and labels on the live homepage.

```bash
RUN_DEPLOY_SMOKE=1 DEPLOY_BASE_URL=https://frago.so python -m unittest tests/test_post_deploy_smoke.py -v
```

Or run the full post-deploy contract in one command:

```bash
bash scripts/post_deploy_check.sh
```

Custom domain example:

```bash
DEPLOY_BASE_URL=https://www.frago.so bash scripts/post_deploy_check.sh
```

## Incident ingest (device-reported errors)

When a layout issue is reported from a real device, create a reproducible evidence bundle:

```bash
bash scripts/ingest_device_report.sh \
	--title "Mobile layout looks deformed" \
	--device "Galaxy S22 / Android / Brave" \
	--url "https://frago.so" \
	--screenshot "/absolute/path/to/screenshot.png" \
	--reporter "Victor" \
	--notes "Cards rendered as plain links on mobile"
```

This generates a folder under `reports/incidents/` with:
- `report.md`
- `live_homepage.html`
- `live_main.css`
- screenshot (if provided)
- `post_deploy_check.log`

Use this process as mandatory input for every production UI issue.
