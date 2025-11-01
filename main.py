from fastapi import FastAPI
from routers import QrCodeController, accountmanagercontroller, attendancecontroller
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI(title="SmartCheck API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # ← VOTRE FRONTEND
    allow_credentials=True,
    allow_methods=["*"],  # GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],  # Tous les headers
)

# Inclusion des routes
app.include_router(QrCodeController.router)
app.include_router(accountmanagercontroller.router)
app.include_router(attendancecontroller.router)

@app.get("/")
def root():
    return {"message": "Bienvenue sur SmartCheck API"}
