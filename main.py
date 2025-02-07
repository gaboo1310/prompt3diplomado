# from fastapi import FastAPI, HTTPException, Request
# from fastapi.middleware.cors import CORSMiddleware
# from dotenv import load_dotenv
# import os
# from openai import OpenAI
# from untils import find_vector_in_redis 

# load_dotenv(override=True)

# OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
# client = OpenAI(api_key=OPENAI_API_KEY)

# app = FastAPI()

# # Enable Cross-Origin Resource Sharing (CORS)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# @app.get("/samples")
# def get_samples():
#     return {"message": "Sample added successfully"}

# @app.post("/generate_message")
# async def generate_message(request: Request):
#     try:
#         body = await request.json()
#         user_input = body.get("message", "")
#         if not user_input:
#             raise HTTPException(status_code=400, detail="No input message provided.")
        
#         completion = client.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=[
#                 {"role": "system", "content": "You are a helpful assistant."},
#                 {"role": "user", "content": user_input}
#             ]
#         )
#         message = completion.choices[0].message.content.strip()
#         return {"message": message}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error generating message: {str(e)}")
    

# @app.post("/generate_message_redis")
# async def generate_message_redis(request: Request):
#     try:
#         print("11111111111111111111111111111")
#         body = await request.json()
#         user_input = body.get("message", "")
#         if not user_input:
#             raise HTTPException(status_code=400, detail="No input mensaje.")

#         print("2222222222222222222222222222")
#         redis_results = find_vector_in_redis(user_input)
#         # if redis_results:
#         #     return {"message": redis_results[0]}  # Se ajusta para devolver el primer resultado correctamente

#         completion = client.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=[
#                 {"role": "system", "content": "eres un asistente, responde al inicio con un hola"},
#                 {"role": "user", "content": f"""entrega la respuesta de forma ordenada, 
#                  es una lista, cada elemento en un salto de linea y en español: {redis_results}"""}
#             ]
#         )
#         message = completion.choices[0].message.content.strip()
#         return {"message": message}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error generating message: {str(e)}")


from fastapi import FastAPI, HTTPException, Request, File, UploadFile, Depends
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from openai import OpenAI
from untils import find_vector_in_redis 
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(override=True)

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=OPENAI_API_KEY)

app = FastAPI()

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

@app.get("/samples")
def get_samples():
    return {"message": "Sample added successfully"}

@app.post("/generate_message")
async def generate_message(request: Request):
    try:
        body = await request.json()
        user_input = body.get("message", "")
        if not user_input:
            raise HTTPException(status_code=400, detail="No input message provided.")
        
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_input}
            ]
        )
        message = completion.choices[0].message.content.strip()
        return {"message": message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating message: {str(e)}")

@app.post("/generate_message_redis")
async def generate_message_redis(request: Request):
    try:
        body = await request.json()
        user_input = body.get("message", "")
        if not user_input:
            raise HTTPException(status_code=400, detail="No input message.")

        redis_results = find_vector_in_redis(user_input)
        
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Eres un asistente, responde al inicio con un hola."},
                {"role": "user", "content": f"""Entrega la respuesta de forma ordenada,
                 es una lista, cada elemento en un salto de línea y en español: {redis_results}"""}
            ]
        )
        message = completion.choices[0].message.content.strip()
        return {"message": message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating message: {str(e)}")

@app.post("/upload_image")
async def upload_image(file: UploadFile = File(...)):
    try:
        file_path = UPLOAD_FOLDER / file.filename
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())
        return {"message": "Imagen guardada exitosamente", "file_path": str(file_path)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al guardar la imagen: {str(e)}")