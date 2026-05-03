"""Scrape URLs and extract readable text for campaign context."""

import logging
import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Tags that typically contain main content
_CONTENT_TAGS = {"p", "h1", "h2", "h3", "h4", "h5", "h6", "li", "td", "th", "blockquote", "figcaption"}

# Tags to remove entirely
_REMOVE_TAGS = {"script", "style", "nav", "footer", "header", "aside", "iframe", "noscript", "svg"}


async def scrape_url(url: str, max_chars: int = 20000) -> dict:
    """Scrape a URL and return extracted text + metadata.

    Returns:
        {"url": str, "title": str, "text": str, "chars": int}
    """
    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
        resp = await client.get(url, headers={
            "User-Agent": "Mozilla/5.0 (compatible; CampaignAI/2.0; +https://github.com/l2dnjsrud/CampaignAI)",
        })
        resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    # Remove noise tags
    for tag in soup.find_all(_REMOVE_TAGS):
        tag.decompose()

    # Extract title
    title = ""
    if soup.title and soup.title.string:
        title = soup.title.string.strip()

    # Extract main content text
    texts = []
    for tag in soup.find_all(_CONTENT_TAGS):
        text = tag.get_text(strip=True)
        if len(text) > 10:  # Skip tiny fragments
            texts.append(text)

    content = "\n".join(texts)[:max_chars]

    return {
        "url": url,
        "title": title,
        "text": content,
        "chars": len(content),
    }
