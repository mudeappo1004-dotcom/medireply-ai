from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from dotenv import load_dotenv
from app.services.ai_service import generate_reply
import os

import sys
import asyncio
from contextlib import asynccontextmanager

# Load Environment Variables
load_dotenv()

app = FastAPI(title="SmartReply AI")

# Mount Static Files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")

from app.services.crawler_service import fetch_naver_reviews

class ReviewRequest(BaseModel):
    review_text: str = None
    tone: str
    url: str = None

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "app_name": "SmartReply AI"})

@app.post("/generate")
async def generate_reply_endpoint(request: ReviewRequest):
    # Case 1: URL provided
    if request.url:
        reviews = await fetch_naver_reviews(request.url, limit=5) # Limit to 5 for speed
        if not reviews:
            return {"reply": "새로운(답글 없는) 리뷰를 찾지 못했습니다. 링크가 정확한지 확인해주세요."}
        
        # Generator for multiple reviews
        results = []
        for review in reviews:
            reply = generate_reply(review, request.tone)
            results.append({"original": review, "reply": reply})
            
        return {"multi_results": results}

    # Case 2: Text provided
    if request.review_text:
        reply = generate_reply(request.review_text, request.tone)
        return {"reply": reply}

    return {"detail": "리뷰 텍스트 또는 URL을 입력해주세요."}
