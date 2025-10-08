from fastapi import FastAPI
from controller.dishes import router as dishes_router

app = FastAPI(title="MatPick API")
app.include_router(dishes_router)


# 선택: 헬스체크
@app.get("/health")
def health():
    return {"ok": True}
