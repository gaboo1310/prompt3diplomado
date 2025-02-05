# Creación y configuración de un entorno virtual en Python 3.10

## 1. Crear un entorno virtual
Para crear un entorno virtual en Python 3.10, ejecuta el siguiente comando en la terminal:

```
py -3.10 -m venv venv

```

## 2. Activar el entorno virtual
En dos consolas diferentes, ejecuta los siguientes comandos según el sistema operativo:

**En Windows (PowerShell):**
```
./venv/Scripts/Activate
```

**En macOS/Linux:**
```
source venv/bin/activate
```

## 3. Instalar los requisitos
Una vez activado el entorno virtual, instala las dependencias del proyecto con:

```
pip install -r requirements.txt
```
### 3.1. si da problemas la instalcion, aplicar y luego reinstalar
pip cache purge

## 4. Ejecutar Streamlit
En una de las consolas, ejecuta Streamlit con el siguiente comando:

```
streamlit run app.py
```

## 5. Ejecutar FastAPI
En la otra consola, ejecuta FastAPI utilizando Uvicorn:

```
uvicorn main:app --reload
```

