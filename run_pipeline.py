"""
Ejecuta el pipeline completo del modelo de riesgo de credito, en orden.

Uso (desde la carpeta raiz del proyecto):
    python run_pipeline.py
"""
import subprocess
import sys

import pandas as pd

PASOS = [
    "0-download-data",
    "1-split-dataset",
    "2-preprocess-dataset-train",
    "3-prepare-dataset-test",
    "4-train-evaluate-models",
    "5-select-best-model",
    "6-score-model",
]


def main():
    for paso in PASOS:
        print(f">> Ejecutando {paso}.py ...")
        subprocess.run([sys.executable, f"src/{paso}.py"], check=True)

    metricas = pd.read_csv("outputs/train/metrics/train_test_metrics.csv")
    print("\nResultados del mejor modelo:")
    for _, fila in metricas.iterrows():
        print(f"   AUC {fila['sample']:<5}: {fila['auc']:.3f}")


if __name__ == "__main__":
    main()
