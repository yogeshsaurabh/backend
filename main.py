import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from prisma import Prisma
from src.admins.router import router as admin_router
from src.auth.router import router as auth_router
from src.config import settings
from src.db.mongodb_utils import close_mongo_connection, connect_to_mongo
from src.live_class.router import router as live_class_router
from src.modules.router import router as module_router
from src.learn.router import router as learn_router
from src.organizations.router import router as organization_router
from src.quiz.router import router as quiz_router
from src.quiz_responses.router import router as quiz_responses_router
from src.students.router import router as student_router
from src.teachers.router import router as teacher_router

app: FastAPI = FastAPI(
    title="Evolve Backend API",
    version="1.0",
    docs_url="/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def init_db_connection():
    await connect_to_mongo()
    db = Prisma(auto_register=True)
    await db.connect()
    app.db = db


@app.on_event("shutdown")
async def close_db_connection():
    await close_mongo_connection()
    await app.db.disconnect()


@app.get("/")
def base_route():
    return {"status": "ok"}


app.include_router(auth_router, tags=["auth"], prefix="/auth")
app.include_router(student_router, tags=["students"], prefix="/student")
app.include_router(teacher_router, tags=["teachers"], prefix="/teacher")
app.include_router(admin_router, tags=["admins"], prefix="/admin")
app.include_router(live_class_router, tags=["live_class"], prefix="/liveclass")
app.include_router(module_router, tags=["modules"], prefix="/module")
app.include_router(quiz_router, tags=["quiz"], prefix="/quiz")

app.include_router(
    organization_router,
    tags=["organizations"],
    prefix="/organization",
)

app.include_router(
    quiz_responses_router,
    tags=["quiz", "responses"],
    prefix="/quiz_response",
)

app.include_router(
    learn_router,
    tags=["learn"],
    prefix="/learn",
)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        reload=settings.DEBUG_MODE,
        port=settings.PORT,
    )
