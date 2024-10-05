from fastapi import FastAPI
from research import router as research_router
from email_generation import router as email_generation_router
from email_review import router as email_review_router
from email_sender import router as email_sender_router
from utils import load_model
import logging

#Logging configuration to check where is the error
logging.basicConfig(level=logging.INFO)

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    """Load the model when the application starts."""
    try:
        load_model()
        logging.info("Application startup complete.")
    except Exception as e:
        logging.error(f"Application startup failed: {e}")

#Routers from other modules
app.include_router(research_router)   #Module1
app.include_router(email_generation_router) #Module2
app.include_router(email_review_router)#Module3
app.include_router(email_sender_router)#Module4

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)
