from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from openai import OpenAI
from pathlib import Path

load_dotenv(override=True)

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=OPENAI_API_KEY)

app = FastAPI()
##--------------------------------------------------------
# Habilitar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directorio para guardar imágenes
UPLOAD_FOLDER = Path("uploaded_images")
UPLOAD_FOLDER.mkdir(exist_ok=True)
##--------------------------------------------------------
@app.get("/samples")
def get_samples():
    return {"message": "Sample added successfully"}

##--------------------------------------------------------
@app.post("/upload_image")
async def upload_image(file: UploadFile = File(...)):
    try:
        file_path = UPLOAD_FOLDER / file.filename
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())
        return {"message": "Imagen guardada exitosamente", "file_path": str(file_path)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al guardar la imagen: {str(e)}")

##--------------------------------------------------------