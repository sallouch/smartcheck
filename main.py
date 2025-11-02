from fastapi import FastAPI
from routers import QrCodeController, accountmanagercontroller, attendancecontroller
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="SmartCheck API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ou ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion des routes
app.include_router(QrCodeController.router)
app.include_router(accountmanagercontroller.router)
app.include_router(attendancecontroller.router)

@app.get("/")
def root():
    return {"message": "Bienvenue sur SmartCheck API"}
