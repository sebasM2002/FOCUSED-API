from fastapi import FastAPI
from routers.admin import admin_router 
app = FastAPI()

app.include_router(admin_router)
