from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.db import get_db
from src.routes import auth_routes, comment_routes, photo_routes, cloudinary_routes, tags
import time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware('http')
async def custom_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    during = time.time() - start_time
    response.headers['performance'] = str(during)
    return response


templates = Jinja2Templates(directory='templates')
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse, description="Paw Prints", tags=["Main index.html"])
async def root(request: Request):
    return templates.TemplateResponse('index.html', {"request": request, "title": "Paw Prints"})


@app.get("/api/healthchecker", tags=["Tools"])
async def healthchecker(db: AsyncSession = Depends(get_db)):
    try:
        # Make request
        result = await db.execute(text("SELECT 1"))
        result = result.fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Database is not configured correctly")
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to the database")


app.include_router(auth_routes.router, prefix="/api")
app.include_router(photo_routes.router, prefix="/api")
app.include_router(comment_routes.router, prefix="/api")
app.include_router(tags.router, prefix="/api")
app.include_router(cloudinary_routes.router, prefix='/api')

