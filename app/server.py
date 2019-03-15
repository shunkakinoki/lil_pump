from starlette.applications import Starlette
from starlette.responses import HTMLResponse, JSONResponse
from starlette.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
import uvicorn, aiohttp, asyncio
from io import BytesIO
import sys
from pathlib import Path
import csv
import time

from fastai import *
from fastai.text import *

export_pkl_url = 'https://www.dropbox.com/s/q568xs2w11tg4yh/lil_pump.pkl?dl=1'
export_pkl_name = 'lil_pump.pkl'

path = Path(__file__).parent

app = Starlette()
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_headers=['X-Requested-With', 'Content-Type'])
app.mount('/static', StaticFiles(directory='app/static'))

async def download_file(url, dest):
    if dest.exists(): return
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.read()
            with open(dest, 'wb') as f: f.write(data)

async def setup_learner():
    await download_file(export_pkl_url, path/export_pkl_name)
    try:
        learn = load_learner(path, export_pkl_name)
        return learn
    except RuntimeError as e:
        if len(e.args) > 0 and 'CPU-only machine' in e.args[0]:
            print(e)
            message = "\n\nThis model was trained with an old version of fastai and will not work in a CPU environment.\n\nPlease update the fastai library in your training environment and export your model again.\n\nSee instructions for 'Returning to work' at https://course.fast.ai."
            raise RuntimeError(message)
        else:
            raise

loop = asyncio.get_event_loop()
tasks = [asyncio.ensure_future(setup_learner())]
learn = loop.run_until_complete(asyncio.gather(*tasks))[0]
loop.close()

@app.route('/')
def index(request):
    html = path/'view'/'index.html'
    return HTMLResponse(html.open().read())

@app.route('/analyze', methods=['POST'])
async def analyze(request):
    data = await request.form()

    return JSONResponse({'result': textResponse(data)})

def textResponse(data):
    words_string = learn.predict(data['predict_text'], int(data['length']), temperature=0.5, min_p=0.001)
    time.sleep(2)

    words = words_string.split()
    for i, word in enumerate(words):
        if word == '(' or word == ')' or word == '"':
            words[i] = ''
        elif word == '.' or word == '?' or word == '!' or word == ';':
            words[i-1]+= words[i]
            words[i] = ''
        elif word[0] == "'":
            words[i-1]+= words[i]
            words[i] = ''

    return ' '.join(words).replace('  ', ' ')

if __name__ == '__main__':
     if 'serve' in sys.argv: uvicorn.run(app=app, host='0.0.0.0', port=5042)
