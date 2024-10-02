from fastapi import FastAPI
from routers.admin import admin_router 
from mangum import Mangum
app = FastAPI()
handler = Mangum(app)

app.include_router(admin_router)
