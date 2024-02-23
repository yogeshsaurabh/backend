from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import DuplicateKeyError

from src.auth.utils import get_current_admin
from src.db.mongodb import get_database
from src.learn.serializers import LessonModelRequest, ModuleModel
from src.learn.service import LearnService
from src.learn.utils import EVOLVE_LEARNING, MODULES
from src.students.utils import get_current_student

router = APIRouter(
    responses={404: {"description": "Not found"}},
)


@router.post("/module/create")
async def create_new_module(
    req: ModuleModel,
    _=Depends(get_current_admin),
    db: AsyncIOMotorClient = Depends(get_database),
):
    try:
        new_module = await LearnService(db=db).create_new_module(req=req)
        return new_module
    except DuplicateKeyError as e:
        return JSONResponse(
            content={"error": e.details, "code": e.code},
            status_code=status.HTTP_400_BAD_REQUEST,
        )


@router.post("/lesson/create")
async def create_new_lesson(
    create_req: LessonModelRequest,
    user: dict = Depends(get_current_student),
    db: AsyncIOMotorClient = Depends(get_database),
):
    learn_service = LearnService(db=db)
    new_lesson = await learn_service.create_lesson(
        user_id=user["id"],
        req=create_req,
    )
    return new_lesson


@router.get("/module", response_model=list[ModuleModel])
async def get_modules(
    _=Depends(get_current_admin),
    db: AsyncIOMotorClient = Depends(get_database),
):
    return await db[EVOLVE_LEARNING][MODULES].find({}).to_list(100)


@router.get("/lesson")
async def get_lesson(
    user: dict = Depends(get_current_student),
    db: AsyncIOMotorClient = Depends(get_database),
):
    learn_service = LearnService(db=db)
    current_lesson = await learn_service.get_current_lesson(user_id=user["id"])

    if not current_lesson:
        return {"msg": "No lessons found"}

    return current_lesson


@router.post("/lesson/finish")
async def finish_lesson(
    user: dict = Depends(get_current_student),
    db: AsyncIOMotorClient = Depends(get_database),
):
    finished_lesson_id = await LearnService(db=db).finish_lesson(user["id"])
    if not finished_lesson_id:
        return {"msg": "No pending lessons."}

    return {"msg": f"marked lesson with id {finished_lesson_id} as finished."}
