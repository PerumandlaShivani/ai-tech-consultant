
import asyncio
import json
from pathlib import Path

import httpx
from bs4 import BeautifulSoup

from sitemap_reader import read_sitemap


OUTPUT_DIR = Path("data/articles")
MAX_ARTICLES = 10  # Start with 10 articles for testing


async def fetch_article(
    client: httpx.AsyncClient,
    url: str,
) -> dict | None:
    """Download one support page and extract its readable text."""

    try:
        response = await client.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove parts that are not article content.
        for element in soup.select(
            "script, style, nav, footer, header"
        ):
            element.decompose()

        title = soup.title.get_text(strip=True) if soup.title else url

        main = soup.select_one(
            "main, article, .solution-content, .content"
        )

        content = main or soup.body or soup
        text = content.get_text(separator="\n", strip=True)

        return {
            "url": url,
            "title": title,
            "content": text,
        }

    except (httpx.HTTPError, ValueError) as error:
        print(f"Failed: {url} — {error}")
        return None


async def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    urls = await read_sitemap()
    article_urls = [
        url for url in urls
        if "/support/solutions/" in url
    ][:MAX_ARTICLES]

    print(f"Testing with {len(article_urls)} articles...")

    headers = {
        "User-Agent": "AI-Tech-Consultant-Student-Project/1.0"
    }

    async with httpx.AsyncClient(
        timeout=30.0,
        follow_redirects=True,
        headers=headers,
    ) as client:
        articles = []

        for url in article_urls:
            article = await fetch_article(client, url)

            if article and article["content"]:
                articles.append(article)
                print(f"Downloaded: {article['title']}")

            # Be polite to the support website.
            await asyncio.sleep(1)

    output_file = OUTPUT_DIR / "articles.json"
    output_file.write_text(
        json.dumps(articles, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"\nSaved {len(articles)} articles to {output_file}")


if __name__ == "__main__":
    asyncio.run(main())
