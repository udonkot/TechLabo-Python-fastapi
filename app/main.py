from fastapi import FastAPI, File, Form, UploadFile, Request, status
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import traceback
import uvicorn
import os
from app.business.azure_document_service import analyze_with_highres

# FastAPIの設定
app = FastAPI()
app.mount("/static", StaticFiles(directory=os.path.join(os.getcwd(), "app/static")), name="static")
templates = Jinja2Templates(directory=os.path.join(os.getcwd(), "app/templates"))


@ app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    print('Request for index page received')
    return templates.TemplateResponse('index.html', {"request": request})


@ app.get('/favicon.ico')
async def favicon():
    file_name = 'favicon.ico'
    file_path = './app/static/' + file_name
    return FileResponse(path=file_path, headers={'mimetype': 'image/vnd.microsoft.icon'})


@ app.post('/hello', response_class=HTMLResponse)
async def hello(request: Request, name: str = Form(...)):
    if name:
        print('Request for hello page received with name=%s' % name)
        return templates.TemplateResponse('hello.html', {"request": request, 'name': name})
    else:
        print('Request for hello page received with no name or blank name -- redirecting')
        return RedirectResponse(request.url_for("index"), status_code=status.HTTP_302_FOUND)


@app.post("/analyze-pdf")
async def analyze_pdf(file: UploadFile = File(...), keyword: str = Form(None)):
    try:
        # PDFファイルを読み込む
        pdf_bytes = await file.read()

        # Azure Document Intelligenceに送信
        is_keyword_found, result = analyze_with_highres(
            model_id="prebuilt-layout",
            pdf_bytes=pdf_bytes,
            search_keyword=keyword
        )

        # 結果を処理して返却
        # print(f"{keyword=}, {is_keyword_found=}, {result=}")
        response_data = {
            "keyword": keyword,
            "isKeywordFound": is_keyword_found,
            "analyzeResult": result
        }
        return JSONResponse(content=response_data)

    except Exception as e:
        print(traceback.format_exc())
        return JSONResponse(content={"error": str(e)}, status_code=500)


if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8000)
