import os
import uvicorn
from fastapi import FastAPI
from openai import OpenAI

app = FastAPI()

@app.get("/")
def ask_ai(prompt: str = "こんにちは！AIです。何かお手伝いしましょうか？"):
    try:
        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return {"response": response.choices[0].message.content}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

