import unittest
from html.parser import HTMLParser
from pathlib import Path


def normalize_space(value: str) -> str:
    return " ".join(value.split())


class IndexParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links = []
        self.buttons = []
        self._anchor_stack = []
        self._button_stack = []

    def handle_starttag(self, tag, attrs):
        data = {"tag": tag, "attrs": dict(attrs), "text": ""}
        if tag == "a":
            self.links.append(data)
            self._anchor_stack.append(data)
        elif tag == "button":
            self.buttons.append(data)
            self._button_stack.append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self._anchor_stack:
            self._anchor_stack.pop()
        elif tag == "button" and self._button_stack:
            self._button_stack.pop()

    def handle_data(self, data):
        for element in self._anchor_stack:
            element["text"] += data
        for element in self._button_stack:
            element["text"] += data


class TestUseCases(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = Path(__file__).resolve().parents[1]
        cls.index_path = root / "index.html"
        cls.html = cls.index_path.read_text(encoding="utf-8")
        cls.parser = IndexParser()
        cls.parser.feed(cls.html)

    def _get_link_by_label(self, label: str):
        normalized = label.upper()
        matches = [
            link
            for link in self.parser.links
            if normalized in normalize_space(link["text"]).upper()
        ]
        self.assertEqual(len(matches), 1, f"Expected one link for {label}")
        return matches[0]

    def test_resume_link(self):
        link = self._get_link_by_label("RESUME")
        attrs = link["attrs"]
        self.assertEqual(
            attrs.get("href"),
            "https://portfolio.frago.so/resume-fragoso.pdf",
        )
        self.assertEqual(attrs.get("target"), "_blank")
        self.assertNotIn("download", attrs)

    def test_portfolio_link(self):
        link = self._get_link_by_label("PORTFOLIO")
        self.assertEqual(link["attrs"].get("href"), "https://portfolio.frago.so/")

    def test_whatsapp_single_occurrence_and_destination(self):
        expected = (
            "https://wa.me/5511970791572"
            "?text=Vi%20o%20seu%20portfolio%20e%20gostaria%20de%20conversar."
        )
        wa_links = [
            link for link in self.parser.links if "wa.me/" in (link["attrs"].get("href") or "")
        ]
        self.assertEqual(len(wa_links), 1)
        self.assertEqual(wa_links[0]["attrs"].get("href"), expected)

    def test_linkedin_link(self):
        link = self._get_link_by_label("LINKEDIN")
        self.assertEqual(link["attrs"].get("href"), "https://www.linkedin.com/in/victorffs/")

    def test_has_exactly_four_quick_cards(self):
        quick_cards = [
            link for link in self.parser.links if "quick-card" in link["attrs"].get("class", "").split()
        ]
        self.assertEqual(len(quick_cards), 4)

    def test_expected_card_labels(self):
        texts = [
            normalize_space(link["text"]).upper()
            for link in self.parser.links
            if "quick-card" in link["attrs"].get("class", "").split()
        ]
        for label in ["RESUME", "PORTFOLIO", "WHATSAPP", "LINKEDIN"]:
            self.assertTrue(any(label in text for text in texts), f"Missing quick card label {label}")

    def test_single_share_button_and_no_icon_action_links(self):
        share_buttons = [
            button
            for button in self.parser.buttons
            if "js-share" in button["attrs"].get("class", "").split()
        ]
        self.assertEqual(len(share_buttons), 1)

        icon_action_links = [
            link for link in self.parser.links if "icon-action" in link["attrs"].get("class", "").split()
        ]
        self.assertEqual(len(icon_action_links), 0)

    def test_demo_text_absent(self):
        forbidden = "You can add your links to this component using the link list above."
        self.assertNotIn(forbidden, self.html)

    def test_has_one_share_button_cta(self):
        share_buttons = [
            button
            for button in self.parser.buttons
            if "js-share" in button["attrs"].get("class", "").split()
        ]
        self.assertEqual(len(share_buttons), 1)
        self.assertIn("SHARE THIS PAGE", normalize_space(share_buttons[0]["text"]).upper())

    def test_has_share_feedback_status_region(self):
        self.assertIn('class="share-feedback"', self.html)
        self.assertIn('role="status"', self.html)


if __name__ == "__main__":
    unittest.main(verbosity=2)
