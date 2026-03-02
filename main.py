import os
import uvicorn
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import google.generativeai as genai
from dotenv import load_dotenv
from typing import List, Dict
import base64

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
async def analyze_english(request: Request, file: UploadFile = File(None)):
    try:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel("models/gemini-2.5-flash")
        
        # Prepare content for analysis
        content = []
        
        # Handle form data (text prompt)
        form_data = await request.form()
        prompt = form_data.get("prompt", "")
        
        # Add text prompt if provided
        if prompt:
            content.append(prompt)
        
        # Add image if uploaded
        if file:
            image_data = await file.read()
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            content.append({
                "inline_data": {
                    "mime_type": file.content_type,
                    "data": image_base64
                }
            })
        
        # Create a prompt to analyze the content
        if prompt and file:
            analysis_prompt = f"""以下の英文と画像を分析してください：
英文: "{prompt}"

以下の内容を日本語で詳しく教えてください：
1. 文型（SVO、SVC、SVなど）
2. 各単語の品詞
3. 各単語の意味
4. 各単語の発音記号

「文型」「品詞」「意味」「発音記号」の見出しで整理して回答してください。"""
        elif prompt:
            analysis_prompt = f"""以下の英文を分析してください：
"{prompt}"

以下の内容を日本語で詳しく教えてください：
1. 文型（SVO、SVC、SVなど）
2. 各単語の品詞
3. 各単語の意味
4. 各単語の発音記号

「文型」「品詞」「意味」「発音記号」の見出しで整理して回答してください。"""
        elif file:
            analysis_prompt = f"""以下の画像に書かれている英文を抽出し、分析してください。

以下の内容を日本語で詳しく教えてください：
1. 文型（SVO、SVC、SVなど）
2. 各単語の品詞
3. 各単語の意味
4. 各単語の発音記号

「文型」「品詞」「意味」「発音記号」の見出しで整理して回答してください。"""
        else:
            return {"error": "テキストまたは画像のいずれかを入力してください"}
        
        # Add the analysis prompt to content
        content.append(analysis_prompt)
        
        response = model.generate_content(content)
        
        # Extract text from image for history title if no prompt provided
        history_title = prompt
        if not prompt and file:
            # Try to extract text from the image for the history title
            try:
                # Use Gemini to extract text from the image
                text_extraction_prompt = "画像に書かれている英文をすべて抽出してください。抽出した英文だけを返してください。"
                text_content = [{
                    "inline_data": {
                        "mime_type": file.content_type,
                        "data": image_base64
                    }
                }, text_extraction_prompt]
                
                text_response = model.generate_content(text_content)
                extracted_text = text_response.text.strip()
                if extracted_text and len(extracted_text) > 0:
                    history_title = extracted_text[:50] + "..." if len(extracted_text) > 50 else extracted_text
                else:
                    history_title = f"画像: {file.filename}"
            except:
                history_title = f"画像: {file.filename}"

        # Store in chat history
        import datetime
        chat_entry = {
            "id": len(chat_history) + 1,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "prompt": prompt,
            "image_filename": file.filename if file else None,
            "history_title": history_title,
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

