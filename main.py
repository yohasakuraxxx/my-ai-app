import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import google.generativeai as genai
from dotenv import load_dotenv
from typing import List, Dict

# Load environment variables from .env file
load_dotenv()

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# In-memory storage for chat history (in production, use a database)
chat_history: List[Dict] = []

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/analyze")
async def analyze_english(request: Request):
    body = await request.body()
    import urllib.parse
    form_data = urllib.parse.parse_qs(body.decode())
    prompt = form_data.get("prompt", [""])[0]
    try:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel("models/gemini-2.5-flash")
        
        # Create a prompt to analyze the English sentence
        analysis_prompt = f"""以下の英文を分析してください：
"{prompt}"

以下の内容を日本語で詳しく教えてください：
1. 文型（SVO、SVC、SVなど）
2. 各単語の品詞
3. 各単語の意味
4. 各単語の発音記号

「文型」「品詞」「意味」「発音記号」の見出しで整理して回答してください。"""
        
        response = model.generate_content(analysis_prompt)
        
        # Store in chat history
        import datetime
        chat_entry = {
            "id": len(chat_history) + 1,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "prompt": prompt,
            "response": response.text
        }
        chat_history.append(chat_entry)
        
        return {"response": response.text, "history_id": chat_entry["id"]}
    except Exception as e:
        return {"error": str(e)}

@app.get("/history")
async def get_history():
    return {"history": chat_history}

@app.get("/history/{history_id}")
async def get_history_item(history_id: int):
    for item in chat_history:
        if item["id"] == history_id:
            return item
    return {"error": "History not found"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

