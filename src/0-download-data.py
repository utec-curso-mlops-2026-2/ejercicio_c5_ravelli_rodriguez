"""
Descarga los datos de entrada desde el bucket S3 del curso.

Los datos NO se versionan en Git: viven en S3 y se descargan a data/in/
solo si todavia no existen en tu computadora.

Uso (desde la carpeta raiz del proyecto):
    python src/download-data.py
"""
import os
import urllib.request

# URL base de los datos en S3 (bucket publico de solo lectura del curso)
DATA_URL_BASE = "https://utec-mlops-datos.s3.us-east-1.amazonaws.com/home-credit/v1"
ARCHIVOS = ["application_data.csv", "columns_description.csv"]
CARPETA_DESTINO = "data/in"


def descargar_datos():
  if os.getcwd().endswith("src"):
    os.chdir("..")
  os.makedirs(CARPETA_DESTINO, exist_ok=True)
  for archivo in ARCHIVOS:
    destino = os.path.join(CARPETA_DESTINO, archivo)
    if os.path.exists(destino):
      print(f"   {archivo}: ya existe, no se descarga")
      continue
    url = f"{DATA_URL_BASE}/{archivo}"
    print(f"   {archivo}: descargando desde {url} ...")
    urllib.request.urlretrieve(url, destino)


if __name__ == "__main__":
    descargar_datos()
