from fastapi import FastAPI
from routers.usuario_route import admin_router 
app = FastAPI()

app.include_router(admin_router)
