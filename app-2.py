from fastapi import FastAPI, UploadFile, File
from playwright.sync_api import sync_playwright
import pandas as pd, tempfile, os
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
BASE_URL = "https://hermes.touramigo.com"
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")


app = FastAPI(title="Supplier Automation API")

def run_playwright_task(df):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        for _, row in df.iterrows():
            page.goto(f"{BASE_URL}/login/form")
            page.fill("input[name='username']", USERNAME)
            page.fill("input[name='password']", PASSWORD)
            page.click("button[type='submit']")
        browser.close()

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # Save CSV temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name
    df = pd.read_csv(tmp_path)

    # Run sync playwright in a thread
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, run_playwright_task, df)

    os.remove(tmp_path)
    return {"status": "ok", "rows": len(df)}
