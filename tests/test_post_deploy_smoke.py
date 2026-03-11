import os
import re
import time
import unittest
from urllib.request import Request, urlopen


class TestPostDeploySmoke(unittest.TestCase):
    @staticmethod
    def _fetch_text(url: str, no_cache: bool = False) -> str:
        fetch_url = url
        if no_cache:
            separator = "&" if "?" in url else "?"
            fetch_url = f"{url}{separator}smoke_ts={time.time_ns()}"

        request = Request(
            fetch_url,
            headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
            },
        )

        with urlopen(request, timeout=15) as response:
            return response.read().decode("utf-8", errors="ignore")

    def test_live_homepage_contract(self):
        if os.getenv("RUN_DEPLOY_SMOKE") != "1":
            self.skipTest("Set RUN_DEPLOY_SMOKE=1 to run live post-deploy smoke tests.")

        base_url = os.getenv("DEPLOY_BASE_URL", "https://frago.so").rstrip("/")
        html = self._fetch_text(base_url, no_cache=True)

        stylesheet_match = re.search(
            r'<link[^>]+rel=["\']stylesheet["\'][^>]+href=["\']([^"\']+)["\']',
            html,
            flags=re.IGNORECASE,
        )
        self.assertIsNotNone(stylesheet_match, "No stylesheet link found in homepage HTML")
        stylesheet_href = stylesheet_match.group(1)

        if stylesheet_href.startswith("http://") or stylesheet_href.startswith("https://"):
            css_url = stylesheet_href
        else:
            css_url = f"{base_url}/{stylesheet_href.lstrip('/')}"

        css = self._fetch_text(css_url, no_cache=True)

        required_snippets = [
            "https://portfolio.frago.so/resume-fragoso.pdf",
            "https://portfolio.frago.so/",
            "https://wa.me/5511970791572?text=Vi%20o%20seu%20portfolio%20e%20gostaria%20de%20conversar.",
            "https://www.linkedin.com/in/victorffs/",
            "RESUME",
            "PORTFOLIO",
            "WHATSAPP",
            "LINKEDIN",
            "Share this page",
        ]

        for snippet in required_snippets:
            self.assertIn(snippet, html)

        required_css_classes = [
            ".quick-grid",
            ".quick-card",
            ".share-cta",
            ".share-feedback",
        ]

        for css_class in required_css_classes:
            self.assertIn(css_class, css)


if __name__ == "__main__":
    unittest.main(verbosity=2)
