import uvicorn
from fastapi import FastAPI, Request, Form, BackgroundTasks
from fastapi.responses import FileResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware import Middleware

from starlette.middleware.sessions import SessionMiddleware
from keebcreator import draw_keeb, draw_heatmap
import os
from pathlib import Path
from PIL import Image
import shelve
import datetime, pytz
import random

middleware = [
    Middleware(SessionMiddleware, secret_key="h34tk33bl0l")
]
app = FastAPI(middleware=middleware)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

FLAG = "STF22{REDACTED}"
KEY = "REDACTED"
ADMIN_TOKEN = "REDACTED"

def hex_to_rgb(hex):
    h = hex.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

admin_token = ""
adminName = 'j4g4h1ms3lf'
adminFrame = hex_to_rgb('#000000')
adminKeys = hex_to_rgb('#dcdedb')
adminText = hex_to_rgb('#000000')
adminKeys = hex_to_rgb('#98b5bb')
with shelve.open('keebdb') as db:
    db[ADMIN_TOKEN] = {
            'name': adminName,
            'frameColor': adminFrame,
            'keyColor': adminKeys,
            'textColor': adminText,
            'specialColor': adminKeys,
            'text': KEY
        }
img = draw_keeb(adminName, adminFrame, adminKeys, adminText, adminKeys)
img.save(f'keebs/keeb-{ADMIN_TOKEN}.png')
img = draw_heatmap(adminName, adminFrame, adminKeys, adminText, adminKeys, KEY)
imgSmall = img.resize((int(img.width / 100), int(img.height / 100)), Image.BILINEAR)
result = imgSmall.resize(img.size, Image.NEAREST)
result.save(f'keebs/heatmap-{ADMIN_TOKEN}.png')

@app.get("/")
def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/menu")
def root(request: Request):
    if 'token' in request.session:
        return templates.TemplateResponse("menu.html", {"request": request})
    else:
        return RedirectResponse('/')


@app.post("/menu")
def keeb(request: Request, token: str = Form(...)):
    with shelve.open('keebdb') as db:
        if token in db:
            # set token cookie
            request.session['token'] = token
            return templates.TemplateResponse("menu.html", {"request": request, "token": token})
        else:
            return templates.TemplateResponse("index.html", {"request": request})


@app.get("/keeb")
def keeb(request: Request):
    # use pathlib to open keeb
    if 'token' in request.session:
        token = request.session['token']
        with shelve.open('keebdb') as db:
            if token in db:
                return FileResponse(f"keebs/keeb-{token}.png")
            else:
                return templates.TemplateResponse("index.html", {"request": request})


@app.get("/build")
def build(request: Request):
    return templates.TemplateResponse("build.html", {"request": request})


@app.post("/build")
def build(request: Request, name: str = Form(...), frameColor: str = Form(...), keyColor: str = Form(...), textColor: str = Form(...), specialColor: str = Form(...)):
    t = datetime.datetime.now(pytz.timezone('Asia/Singapore'))
    seed = int(t.timestamp())
    random.seed(seed)
    token = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=16))
    with shelve.open('keebdb') as db:
        db[token] = {
            'name': name,
            'frameColor': hex_to_rgb(frameColor),
            'keyColor': hex_to_rgb(keyColor),
            'textColor': hex_to_rgb(textColor),
            'specialColor': hex_to_rgb(specialColor),
            'text': 'default'
        }
    img = draw_keeb(name, hex_to_rgb(frameColor), hex_to_rgb(keyColor), hex_to_rgb(textColor), hex_to_rgb(specialColor))
    img.save(f'keebs/keeb-{token}.png')
    request.session['token'] = token
    return templates.TemplateResponse("build.html", {"request": request, "resp": "Success!", "token": token})

@app.get('/rebuild')
def rebuild(request: Request):
    if 'token' in request.session:
        return templates.TemplateResponse("rebuild.html", {"request": request})

@app.post('/rebuild')
def rebuild(request: Request, frameColor: str = Form(...), keyColor: str = Form(...), textColor: str = Form(...), specialColor: str = Form(...)):
    if 'token' in request.session:
        token = request.session['token']
        with shelve.open('keebdb') as db:
            if token in db:
                img = draw_keeb(db[token]['name'], hex_to_rgb(frameColor), hex_to_rgb(keyColor), hex_to_rgb(textColor), hex_to_rgb(specialColor))
                img.save(f'keebs/keeb-{token}.png')
                db[token] = {
                    'name': db[token]['name'],
                    'frameColor': hex_to_rgb(frameColor),
                    'keyColor': hex_to_rgb(keyColor),
                    'textColor': hex_to_rgb(textColor),
                    'specialColor': hex_to_rgb(specialColor),
                    'text': db[token]['text']
                }
                return templates.TemplateResponse("rebuild.html", {"request": request, "resp": "Success!"})
            else:
                return templates.TemplateResponse("index.html", {"request": request})

@app.get('/heatmap/generate')
def generate_heatmap(request: Request):
    if 'token' in request.session:
        return templates.TemplateResponse("heatmap-gen.html", {"request": request})


@app.post('/heatmap/generate')
def generate_heatmap(request: Request, text: str = Form(...)):
    if 'token' in request.session:
        token = request.session['token']
        with shelve.open('keebdb') as db:
            if token in db:
                name = db[token]['name']
                frameColor = db[token]['frameColor']
                keyColor = db[token]['keyColor']
                textColor = db[token]['textColor']
                specialColor = db[token]['specialColor']
                img = draw_heatmap(name, frameColor, keyColor, textColor, specialColor, text.upper())
                imgSmall = img.resize((int(img.width / 100), int(img.height / 100)), Image.BILINEAR)
                result = imgSmall.resize(img.size, Image.NEAREST)
                result.save(f'keebs/heatmap-{token}.png')
                db[token] = {
                    'name': name,
                    'frameColor': frameColor,
                    'keyColor': keyColor,
                    'textColor': textColor,
                    'specialColor': specialColor,
                    'text': text.upper()
                }
                return FileResponse(f"keebs/heatmap-{token}.png")


@app.get('/heatmap/view')
def heatmap(request: Request, background_tasks: BackgroundTasks): 
    if 'token' in request.session:
        token = request.session['token']
        with shelve.open('keebdb') as db:
            if token in db:
                try:
                    img = Image.open(f'keebs/heatmap-{token}.png')
                    img.close()
                except FileNotFoundError:
                    return RedirectResponse('/heatmap/generate')
                return FileResponse(f"keebs/heatmap-{token}.png")
            else:
                return templates.TemplateResponse("index.html", {"request": request})

@app.get('/text')
def flag(request: Request):
    if 'token' in request.session:
        return templates.TemplateResponse("flag.html", {"request": request})

@app.post('/text')
def flag(request: Request, text: str = Form(...)):
    if 'token' in request.session:
        with shelve.open('keebdb') as db:
            token = request.session['token']
            if token in db:
                if token == ADMIN_TOKEN and text.upper() == KEY:
                    return templates.TemplateResponse("flag.html", {"request": request, "word": text, "flag": FLAG})
                elif text.upper() == db[token]['text']:
                    return templates.TemplateResponse("flag.html", {"request": request, "word": text})
    return templates.TemplateResponse("flag.html", {"request": request})

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)