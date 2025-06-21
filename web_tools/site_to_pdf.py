import asyncio
from io import BytesIO
from typing import List, Set, Tuple
from urllib.parse import urljoin, urlparse

from PyPDF2 import PdfMerger
from playwright.async_api import async_playwright


async def crawl_website(start_url: str, max_depth: int) -> bytes:
    """Crawl links starting from ``start_url`` up to ``max_depth`` and
    return a single PDF combining all visited pages."""
    visited: Set[str] = set()
    queue: List[Tuple[str, int]] = [(start_url, 0)]
    merger = PdfMerger()

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        while queue:
            url, depth = queue.pop(0)
            if url in visited or depth > max_depth:
                continue
            visited.add(url)
            page = await browser.new_page()
            try:
                await page.goto(url, wait_until="networkidle")
                pdf_bytes = await page.pdf(print_background=True)
                merger.append(BytesIO(pdf_bytes))
                if depth < max_depth:
                    hrefs = await page.eval_on_selector_all(
                        "a[href]",
                        "els => els.map(e => e.getAttribute('href'))",
                    )
                    for href in hrefs:
                        if not href:
                            continue
                        link = href if href.startswith("http") else urljoin(url, href)
                        if urlparse(link).netloc != urlparse(start_url).netloc:
                            continue
                        link = link.split("#")[0]
                        if link not in visited:
                            queue.append((link, depth + 1))
            except Exception as exc:
                print(f"Failed to process {url}: {exc}")
            finally:
                await page.close()
        await browser.close()

    output = BytesIO()
    merger.write(output)
    merger.close()
    return output.getvalue()


async def save_website_pdf(url: str, depth: int, output_path: str) -> None:
    pdf_content = await crawl_website(url, depth)
    with open(output_path, "wb") as f:
        f.write(pdf_content)


def main() -> None:
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description="Crawl a website and save pages as a single PDF."
    )
    parser.add_argument("url", help="Starting URL")
    parser.add_argument("depth", type=int, help="Link depth to follow")
    parser.add_argument(
        "output", nargs="?", default="site.pdf", help="Output PDF file"
    )
    if len(sys.argv) == 1:
        parser.print_help()
        return
    args = parser.parse_args()

    asyncio.run(save_website_pdf(args.url, args.depth, args.output))


if __name__ == "__main__":
    main()
