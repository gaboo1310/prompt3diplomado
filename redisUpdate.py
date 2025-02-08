

import os
import pandas as pd
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.vectorstores.redis import Redis
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from dotenv import load_dotenv

load_dotenv(override=True)


input_dir = './HAM20V2_metadata.csv'  # Archivo CSV de entrada
output_dir = './salidaTXT'

##--------------------------------------------------------
# Crear el directorio si no existe, toma el csv y lo divide en txt
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


##--------------------------------------------------------

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



##--------------------------------------------------------
# Iterar sobre el DataFrame y crear un archivo .txt para cada dato
for _, row in df.iterrows():
    image_id = row['image_id'].replace("/", "-")  
    file_name = f"{image_id}.txt"
    file_path = os.path.join(output_dir, file_name)
    
    # Escribir los detalles en un archivo .txt
    with open(file_path, 'w') as file:
        file.write(create_lesion_details_text(row))

output_dir  # Retornar el directorio donde se guardan los archivos
embeddingTxt(output_dir)

##--------------------------------------------------------





