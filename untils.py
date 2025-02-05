
import os
import array
from openai import OpenAI
from redis import Redis
from redis.commands.search.query import Query

def find_vector_in_redis(query):
    try:
        # Cargar las credenciales desde las variables de entorno
        OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
        redis_username = os.getenv('redis_username')
        redis_password = os.getenv('redis_password')
        redis_host = os.getenv('redis_host')
        redis_port = os.getenv('redis_port')
        redis_db = os.getenv('redis_db')
        redis_index = os.getenv("redis_index")
        VECTOR_FIELD_NAME = 'content_vector'

        # Crear la URL de conexión a Redis
        url = f"redis://{redis_username}:{redis_password}@{redis_host}:{redis_port}/{redis_db}"
        r = Redis.from_url(url=url)

        # Verificar conexión a Redis
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
