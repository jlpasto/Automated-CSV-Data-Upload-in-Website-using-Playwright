from fastapi import FastAPI, UploadFile
import asyncio
from playwright.sync_api import sync_playwright

app = FastAPI()

def run_playwright():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://example.com")
        title = page.title()
        browser.close()
        return title

@app.post("/upload")
async def upload_file(file: UploadFile):
    # Run Playwright in a separate thread
    result = await asyncio.to_thread(run_playwright)
    return {"page_title": result}
