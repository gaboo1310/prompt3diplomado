# import redis
# import pandas as pd
# import json
# import os

# from dotenv import load_dotenv
# load_dotenv(override=True)


# def upload_csv_to_redis(file_path, key_prefix='csv'):

#     OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
#     redis_username = os.getenv('redis_username')
#     redis_password = os.getenv('redis_password')
#     redis_host = os.getenv('redis_host')
#     redis_port = os.getenv('redis_port')
#     redis_db = os.getenv('redis_db')
#     redis_index = os.getenv("redis_index")
    
        
#     try:
#         # Crear conexión a Redis
#         redis_client = redis.Redis(
#             host=redis_host,  # Cambia esto según tu configuración
#             port=redis_port,
#             decode_responses=True
#         )
        
#         # Leer el CSV con pandas
#         df = pd.read_csv(file_path, sep=';')  # Usando ';' como separador basado en tu archivo original
        
#         # Convertir el DataFrame a una lista de diccionarios
#         records = df.to_dict(orient='records')
        
#         # Generar una key única para el dataset
#         dataset_key = f"{key_prefix}:dataset"
        
#         # Almacenar metadatos sobre el dataset
#         redis_client.hset(dataset_key, 'filename', file_path)
#         redis_client.hset(dataset_key, 'total_records', len(records))
        
#         # Almacenar cada registro como un hash separado
#         for index, record in enumerate(records):
#             # Convertir valores no serializables a strings
#             record_safe = {k: str(v) if not isinstance(v, (str, int, float)) else v 
#                            for k, v in record.items()}
            
#             # Crear una key única para cada registro
#             record_key = f"{key_prefix}:record:{index}"
            
#             # Almacenar el registro como un hash
#             redis_client.hmset(record_key, record_safe)
        
#         print(f"Archivo CSV '{file_path}' cargado exitosamente en Redis.")
#         print(f"Total de registros: {len(records)}")
        
#         return True
        
#     except Exception as e:
#         print(f"Error al subir el archivo CSV: {str(e)}")
#         return False

# def retrieve_csv_from_redis(key_prefix='csv'):
#     """
#     Recupera todos los registros de un dataset CSV almacenado en Redis

#     Args:
#         key_prefix (str, optional): Prefijo usado al cargar el CSV. Defaults a 'csv'.

#     Returns:
#         list: Lista de registros recuperados
#     """
#     try:
#         redis_client = redis.Redis(
#             host='localhost',
#             port=6379,
#             decode_responses=True
#         )
        
#         # Obtener metadatos del dataset
#         dataset_key = f"{key_prefix}:dataset"
#         filename = redis_client.hget(dataset_key, 'filename')
#         total_records = int(redis_client.hget(dataset_key, 'total_records'))
        
#         # Recuperar todos los registros
#         records = []
#         for i in range(total_records):
#             record_key = f"{key_prefix}:record:{i}"
#             record = redis_client.hgetall(record_key)
#             records.append(record)
        
#         print(f"Recuperados {len(records)} registros del dataset.")
#         return records
    
#     except Exception as e:
#         print(f"Error al recuperar el dataset: {str(e)}")
#         return []

# # Ejemplo de uso
# if __name__ == "__main__":
#     # Subir el archivo CSV
#     upload_csv_to_redis('HAM20_metadata.csv')
    
#     # Recuperar los datos
#     retrieved_data = retrieve_csv_from_redis()
    
#     # Opcional: convertir de vuelta a DataFrame
#     import pandas as pd
#     df_retrieved = pd.DataFrame(retrieved_data)
#     print(df_retrieved.head())



import os
import pandas as pd

# from langchain import LLMChain
# import array
# import openai
# import os
# import requests
# import json
# import redis
# import array
# from redis import Redis
# from redis.commands.search.query import Query
# from langchain_community.embeddings import OpenAIEmbeddings
# from langchain_community.document_loaders import TextLoader
# from langchain_text_splitters import CharacterTextSplitter
# import warnings



from langchain_community.embeddings import OpenAIEmbeddings
from langchain.vectorstores.redis import Redis
from langchain.document_loaders import TextLoader
from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain.text_splitter import CharacterTextSplitter
import numpy as np
import openai
from redis.commands.search.query import Query
import redis
from dotenv import load_dotenv

load_dotenv(override=True)


input_dir = './HAM20V2_metadata.csv'  # Archivo CSV de entrada
output_dir = './salidaTXT'


# Crear el directorio si no existe
os.makedirs(output_dir, exist_ok=True)
df = pd.read_csv(input_dir, sep=";")
df.columns = df.columns.str.strip()

def embeddingTxt(input_dir):

    # Obtener credenciales desde variables de entorno
    gpt_key = os.getenv('OPENAI_API_KEY')
    redis_username = os.getenv('redis_username')
    redis_password = os.getenv('redis_password')
    redis_host = os.getenv('redis_host')
    redis_port = os.getenv('redis_port')
    redis_db = os.getenv('redis_db')
    redis_index = os.getenv("redis_index")

    # Crear embeddings usando la API de OpenAI
    embeddings = OpenAIEmbeddings(openai_api_key=gpt_key)

    # Iterar sobre cada archivo en el directorio y cargarlo a Redis
    for filename in sorted(os.listdir(input_dir)):
        if filename.endswith(".txt"):
            file_path = os.path.join(input_dir, filename)

            # Cargar el documento desde el archivo de texto
            loader = TextLoader(file_path, encoding="utf-8")
            documents = loader.load()

            # Dividir el documento en fragmentos de tamaño adecuado para embeddings
            text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
            docs = text_splitter.split_documents(documents)

           
            vectorstore = Redis(
                embedding=embeddings,
                redis_url=f"redis://{redis_username}:{redis_password}@{redis_host}:{redis_port}/{redis_db}",
                index_name=redis_index
            )
            vectorstore.add_documents(docs)
            

            print(f"Documentos del archivo '{filename}' cargados exitosamente en Redis.")

    print("Todos los archivos han sido procesados y cargados en Redis.")
    
# Función para crear el contenido del archivo de texto desde la fila de datos
def create_lesion_details_text(row):
    return (f"Lesion ID: {row['lesion_id']}\n"
            f"Image ID: {row['image_id']}\n"
            f"Diagnosis: {row['dx']}\n"
            f"Diagnosis Type: {row['dx_type']}\n"
            f"Age: {row['age']}\n"
            f"Sex: {row['sex']}\n"
            f"Localization: {row['localization']}\n"
            f"i64: {row['i64']}\n")




# Iterar sobre el DataFrame y crear un archivo .txt para cada imagen
for _, row in df.iterrows():
    image_id = row['image_id'].replace("/", "-")  # Reemplazar barras en nombres para evitar problemas en nombres de archivos
    file_name = f"{image_id}.txt"
    file_path = os.path.join(output_dir, file_name)
    
    # Escribir los detalles en un archivo .txt
    with open(file_path, 'w') as file:
        file.write(create_lesion_details_text(row))

output_dir  # Retornar el directorio donde se guardan los archivos
embeddingTxt(output_dir)








