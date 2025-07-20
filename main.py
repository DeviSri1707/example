from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
import io
import re

app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    try:
        content = await file.read()
        df = pd.read_csv(io.StringIO(content.decode("utf-8")), skip_blank_lines=True)

        # Standardize column names (remove leading/trailing spaces and lower-case them)
        df.columns = [col.strip().lower() for col in df.columns]

        # Try to find relevant columns
        category_col = next((col for col in df.columns if "category" in col), None)
        amount_col = next((col for col in df.columns if "amount" in col or "spent" in col), None)

        if not category_col or not amount_col:
            return JSONResponse(status_code=400, content={
                "error": "Required columns not found in CSV."
            })

        # Clean up category column
        df[category_col] = df[category_col].astype(str).str.strip().str.lower()

        # Filter for "food" category
        food_df = df[df[category_col] == "food"]

        # Clean and convert amount column
        def parse_amount(x):
            if pd.isna(x):
                return 0.0
            # Remove currency symbols, commas, and spaces
            x = str(x)
            x = re.sub(r'[^\d\.\-]', '', x.replace(",", ""))
            try:
                return float(x)
            except ValueError:
                return 0.0

        food_df[amount_col] = food_df[amount_col].apply(parse_amount)

        total = round(food_df[amount_col].sum(), 2)

        return {
            "answer": total,
            "email": "23f3002853@ds.study.iitm.ac.in",  # Replace with your actual email
            "exam": "tds-2025-05-roe"
        }

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

