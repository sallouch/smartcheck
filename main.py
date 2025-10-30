from fastapi import FastAPI
from routers import QrCodeController, accountmanagercontroller, attendancecontroller

app = FastAPI(title="SmartCheck API")

# Inclusion des routes
app.include_router(QrCodeController.router)
app.include_router(accountmanagercontroller.router)
app.include_router(attendancecontroller.router)

@app.get("/")
def root():
    return {"message": "Bienvenue sur SmartCheck API"}
if __name__ == "__main__":
    main()
print
