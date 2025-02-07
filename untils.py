
import os
import array
from openai import OpenAI
from redis import Redis
from redis.commands.search.query import Query
import base64

import base64
from PIL import Image
import io
import os
import csv
import glob

import base64
from openai import OpenAI

from pathlib import Path

# Definir la carpeta donde se guardarán las imágenes temporales
TEMP_IMAGE_PATH = Path("uploaded_images")
TEMP_IMAGE_PATH.mkdir(exist_ok=True)  # Asegura que la carpeta existe

def convert_image_to_base64(image_file):
    """ Convierte una imagen subida a base64. """
    temp_file_path = TEMP_IMAGE_PATH / "file.jpg"  # Guardar con un nombre fijo
    with open(temp_file_path, "wb") as f:
        f.write(image_file)

    with open(temp_file_path, "rb") as f:
       
        return base64.b64encode(f.read()).decode("utf-8")
    
    
def optimize_image(image_file):
    temp_file_path = TEMP_IMAGE_PATH / "file.jpg"  # Guardar con un nombre fijo
    with open(temp_file_path, "wb") as f:
        f.write(image_file)

    with open(temp_file_path, "rb") as f:
    
        try:
            with Image.open(temp_file_path) as img:
                # Convertir a RGB si es necesario (manteniendo el color)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                
                new_img = Image.new('RGB', (64, 64), 'white')
                img.thumbnail((64, 64), Image.Resampling.LANCZOS)
                
                position = ((64 - img.size[0]) // 2, (64 - img.size[1]) // 2)
                new_img.paste(img, position)
                
                buffer = io.BytesIO()
                new_img.save(buffer, format='JPEG', quality=70, optimize=True)
                buffer.seek(0)
                
                base64_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
                
                return base64_image
        except Exception as e:
            return f"Error procesando {temp_file_path}: {str(e)}"
    
    

def analyze_image_with_chatgpt(image_bytes):  
    #base64_image = convert_image_to_base64(image_bytes)
    base64_image= optimize_image(image_bytes)
    
    with open("nombre_archivo", "w", encoding="utf-8") as archivo:
        archivo.write(base64_image)
        
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "desde un punto de vista academico, que observar en esta foto de un lunar (no incluyas la palabra academico en tu respuesta, en español)"},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
                ],
            }
        ],
    )
    
    
    respuesta = find_vector_in_redis(base64_image)
    return respuesta
    # return response.choices[0].message.content








def find_vector_in_redis(query):
    try:


        OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
        redis_username = os.getenv('redis_username')
        redis_password = os.getenv('redis_password')
        redis_host = os.getenv('redis_host')
        redis_port = os.getenv('redis_port')
        redis_db = os.getenv('redis_db')
        redis_index = os.getenv("redis_index")
        VECTOR_FIELD_NAME = 'content_vector'

        url = f"redis://{redis_username}:{redis_password}@{redis_host}:{redis_port}/{redis_db}"
        r = Redis.from_url(url=url)


        try:
            if r.ping():
                print("Conexión exitosa con Redis")
            else:
                print("SIN CONEXIÓN con Redis")
                return []
        except Exception as e:
            print(f" Error conectando a Redis: {e}")
            return []

        # Configurar el cliente de OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)

        # Generar el embedding utilizando OpenAI
        print("🔍 Solicitando embedding a OpenAI...")
        response = client.embeddings.create(
            input=query,
            model="text-embedding-ada-002",
        )
        print("OpenAI respondió correctamente.")

        # Verificar que OpenAI devolvió datos válidos
        if not response.data:
            print("OpenAI no devolvió datos válidos")
            return []

        # Obtener el embedding generado
        embedding_vector = response.data[0].embedding
        print(f"Embedding generado (longitud {len(embedding_vector)}): {embedding_vector[:5]}...")

        # Convertir a binario para Redis
        embedded_query = array.array('f', embedding_vector).tobytes()
        print(f"Embedding convertido a binario: {embedded_query[:10]}...")

        # Configurar la consulta para Redis
        top_k = 1  # Número de resultados más cercanos
        q = Query(f'*=>[KNN {top_k} @{VECTOR_FIELD_NAME} $vec_param AS vector_score]') \
            .sort_by('vector_score') \
            .paging(0, top_k) \
            .return_fields('filename', 'text_chunk', 'text_chunk_index', 'content', 'vector_score') \
            .dialect(2)

        params_dict = {"vec_param": embedded_query}
        print(f"Ejecutando consulta en Redis con Query: {q}")

        # Ejecutar la consulta en Redis
        try:
            results = r.ft(redis_index).search(q, query_params=params_dict)
        except Exception as e:
            print(f"Error en la consulta a Redis: {e}")
            return []

        print(f"Resultados obtenidos de Redis: {results}")

        # Verificar si se encontraron documentos
        if results.total == 0:
            print("No se encontraron documentos en Redis.")
            return []

        print("444444444444444444444444444444")
        contents = [str(doc.content) for doc in results.docs]
        print(contents)
        return contents

    except Exception as e:
        print(f"Error en find_vector_in_redis: {str(e)}")
        return []
