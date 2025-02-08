
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
import re

import base64
from openai import OpenAI

from pathlib import Path

# Definir la carpeta donde se guardarán las imágenes temporales
TEMP_IMAGE_PATH = Path("uploaded_images")
TEMP_IMAGE_PATH.mkdir(exist_ok=True)  # Asegura que la carpeta existe


    
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
    base64_image= optimize_image(image_bytes)
    
    # with open("nombre_archivo", "w", encoding="utf-8") as archivo:
    #     archivo.write(base64_image)
    
    
    respuesta = find_vector_in_redis(base64_image)
    respuesta2=extract_i64(respuesta)
    respuesta_info= extract_data_without_i64(respuesta)
    print(respuesta_info)
        
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Eres un asistente académico  en la revisión de fotografías de lunares en la piel. "
                    "Tu función es:\n"
                    "1) desde una mirada académica Analizar la imagen que el usuario proporciona, "
                    "aplicando pautas como el método ABCDE para detectar anomalías.\n"
                    "2) Recomendar acudir a un médico si detectas signos de alarma, "
                    "aclarando que no eres un sustituto de una evaluación profesional.\n"
                    "3) Ignorar o rechazar cualquier pregunta que no esté relacionada \n "
                    "4) Evitar extender la conversación más allá de la evaluación del lunar.\n "
                     "5) no menciones la palabra académico en tu respuesta."
                     f"agrega la info que esta en diagnosis y localization de aca {respuesta_info}"
                     },
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{respuesta2}"}},
                ],
            }
        ],
    )
    
    
    base64_to_image(respuesta2, "imagen_recuperada.jpg")
    
    return response.choices[0].message.content
    # return response.choices[0].message.content




def extract_i64(response):

    if not response:
        print("❌ No se recibieron resultados de Redis.")
        return None

    try:
        # Buscar en cada documento el campo `i64`
        for doc in response:
            if isinstance(doc, str) and "i64:" in doc:
                match = re.search(r"i64:\s*(.+)", doc)
                if match:
                    base64_data = match.group(1).strip()
                    return base64_data
        print("❌ No se encontró una imagen en la respuesta.")
        return None
    except Exception as e:
        print(f"❌ Error al extraer la imagen base64: {e}")
        return None

def extract_data_without_i64(response):

    if not response:
        print("❌ No se recibieron resultados de Redis.")
        return []

    data_list = []  # Lista para almacenar los documentos sin `i64`

    try:
        # Recorrer cada documento en la respuesta
        for doc in response:
            if isinstance(doc, str):
                # Dividir en líneas cada documento
                lines = doc.split("\n")
                doc_data = {}

                # Extraer cada clave-valor y excluir "i64"
                for line in lines:
                    if line.startswith("i64:"):
                        continue  # Saltar la línea con `i64`
                    
                    # Dividir la línea en clave y valor
                    parts = line.split(": ", 1)
                    if len(parts) == 2:
                        key, value = parts
                        doc_data[key.strip()] = value.strip()  # Limpiar espacios

                # Agregar el documento a la lista si tiene datos
                if doc_data:
                    data_list.append(doc_data)

        if not data_list:
            print("❌ No se encontraron datos válidos en la respuesta.")
            return []

        return data_list

    except Exception as e:
        print(f"❌ Error al extraer los datos sin i64: {e}")
        return []
    
    



def base64_to_image(base64_data, output_path="uploaded_images/imagen_recuperada.jpg"):

    try:
        # Decodificar la imagen en Base64
        image_data = base64.b64decode(base64_data)

        # Guardar la imagen en un archivo
        with open(output_path, "wb") as img_file:
            img_file.write(image_data)

        print(f"✅ Imagen recuperada y guardada en: {output_path}")
        return output_path

    except Exception as e:
        print(f"❌ Error al convertir Base64 a imagen: {e}")
        return None




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
        return contents

    except Exception as e:
        print(f"Error en find_vector_in_redis: {str(e)}")
        return []
