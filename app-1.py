from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from playwright.async_api import async_playwright
import pandas as pd
import csv, json, os
from dotenv import load_dotenv
from tempfile import NamedTemporaryFile
import os
import tempfile, os, traceback
import chardet

# Load environment variables
load_dotenv()
BASE_URL = "https://hermes.touramigo.com"
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

app = FastAPI(title="Supplier Automation API")

# -------------------- File Parsing --------------------
def parse_file_to_json_list(file_path: str):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".csv":
        return csv_to_json_list(file_path)
    elif ext in [".xls", ".xlsx"]:
        df = pd.read_excel(file_path)
        df.to_json("output.json", orient="records", force_ascii=False, indent=2)
        return df.fillna("").to_dict(orient="records")
    else:
        raise ValueError("Unsupported file extension. Only .csv, .xls, .xlsx are allowed.")

def csv_to_json_list(csv_file_path: str):
    with open(csv_file_path, mode="r", encoding="utf-8", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        items = [dict(row) for row in reader]
        with open("output.json", "w", encoding="utf-8") as jsonfile:
            json.dump(items, jsonfile, ensure_ascii=False, indent=2)
    return items

# -------------------- Playwright Login --------------------
def login(context, page):
    page.goto(f"{BASE_URL}/login/form")
    page.fill("input[name='username']", USERNAME)
    page.fill("input[name='password']", PASSWORD)
    page.click("button[type='submit']")
    page.wait_for_load_state("networkidle")
    context.storage_state(path="session.json")
    print("Logged in and session saved.")

def is_logged_in(page):
    page.goto(BASE_URL)
    try:
        page.wait_for_selector("div.salutation-container", timeout=5000)
        return True
    except Exception:
        return False

# -------------------- API Endpoint --------------------
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Save uploaded file temporarily
        ext = os.path.splitext(file.filename)[1] or ".csv"
        with NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            contents = await file.read()
            if not contents:
                raise HTTPException(status_code=400, detail="Uploaded file is empty")
            tmp.write(contents)
            tmp_path = tmp.name

        # Detect encoding
        with open(tmp_path, "rb") as f:
            raw = f.read(10000)
        result = chardet.detect(raw)
        encoding = result["encoding"] or "utf-8"

        # Parse CSV
        # Try reading CSV first
        try:
            df = pd.read_csv(tmp_path, encoding=encoding)
        except Exception as e_csv:
            # Try Excel if CSV fails
            try:
                df = pd.read_excel(tmp_path)
            except Exception as e_xls:
                raise HTTPException(
                    status_code=400,
                    detail=f"Cannot parse file as CSV ({str(e_csv)}) or Excel ({str(e_xls)})"
                )


        # Parse into JSON list
        try:
            records = parse_file_to_json_list(tmp_path)
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"File parsing error: {str(e)}")

        # Run playwright automation
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)  # set headless=True in production
            # context = browser.new_context()
            #page = context.new_page()
            page = await browser.new_page()

            for _, row in df.iterrows():
                await page.goto("https://example.com/form")
                await page.fill("#name", str(row["Name"]))
                await page.fill("#email", str(row["Email"]))
                await page.click("#submit")

            await browser.close()

        return {"status": "ok", "rows": len(df)}

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    

    finally:
        if "tmp_path" in locals() and os.path.exists(tmp_path):
            os.remove(tmp_path)
