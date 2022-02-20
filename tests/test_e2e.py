# import asyncio
# from playwright.async_api import async_playwright
import pytest
from starlette.testclient import TestClient
import uvicorn

from web.api import app

@pytest.fixture
def test_app():
    with uvicorn.run(app, host='0.0.0.0', port=3001) as client:
        yield client

def test_example_is_working(test_app, page):
    page.goto("http://localhost:3001")
    assert page.title() == "set game"

# async def main():
#     async with async_playwright() as p:
#         browser = await p.chromium.launch()
#         page = await browser.new_page()
#         await page.goto("http://playwright.dev")
#         print(await page.title())
#         await browser.close()

# asyncio.run(main())