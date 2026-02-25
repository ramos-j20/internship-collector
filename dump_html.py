import asyncio
from playwright.async_api import async_playwright

async def dump_html(url, filename):
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=["--disable-blink-features=AutomationControlled"])
        page = await browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        await page.goto(url, wait_until="domcontentloaded", timeout=15000)
        await page.wait_for_timeout(3000) # Give it 3 extra seconds to render the SPA
        content = await page.content()
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        await browser.close()
        print(f"Dumped {url} to {filename}")

async def main():
    await dump_html("https://emprego.sapo.pt/offers?q=trainee%20OR%20estagio", "debug_sapo_spa.html")
    await dump_html("https://expressoemprego.pt/ofertas?q=est%C3%A1gio+OR+trainee", "debug_expresso_spa.html")

if __name__ == "__main__":
    asyncio.run(main())
