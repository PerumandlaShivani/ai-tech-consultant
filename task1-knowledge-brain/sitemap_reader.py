
import asyncio
import xml.etree.ElementTree as ET

import httpx


SITEMAP_URL = (
    "https://support.brilliantdirectories.com/support/sitemap.xml"
)


async def read_sitemap() -> list[str]:
    """Download the sitemap and extract page URLs."""

    headers = {
        "User-Agent": "AI-Tech-Consultant-Student-Project/1.0"
    }

    async with httpx.AsyncClient(
        timeout=30.0,
        follow_redirects=True,
        headers=headers,
    ) as client:
        response = await client.get(SITEMAP_URL)
        response.raise_for_status()

    root = ET.fromstring(response.content)

    urls = [
        element.text.strip()
        for element in root.iter()
        if element.tag.endswith("loc") and element.text
    ]

    return urls


async def main() -> None:
    try:
        urls = await read_sitemap()

        print(f"Total URLs found: {len(urls)}")
        print("\nFirst 10 URLs:")

        for url in urls[:10]:
            print(url)

    except (httpx.HTTPError, ET.ParseError) as error:
        print(f"Could not read sitemap: {error}")


if __name__ == "__main__":
    asyncio.run(main())
