# Modelo de riesgo de crédito · Plantilla del curso MLOps (UTEC Posgrado)

Pipeline de Machine Learning que estima la probabilidad de incumplimiento de pago de un solicitante de crédito, usando un Random Forest.

## Estructura

```
src/0-download-data.py              descarga los datos de entrada desde S3 a data/in/
src/1-split-dataset.py              separa train (70%) y test (30%)
src/2-preprocess-dataset-train.py   imputación, análisis bivariado y selección de variables
src/3-prepare-dataset-test.py       aplica el preprocesamiento a test
src/4-train-evaluate-models.py      entrena con GridSearchCV y valida con AUC
src/5-select-best-model.py          elige el mejor modelo y calcula AUC en train y test
src/6-score-model.py                genera las predicciones (scoring)
run_pipeline.py                     ejecuta los 6 pasos en orden
```

## Cómo ejecutarlo

```bash
pip install -r requirements.txt
python run_pipeline.py
```

La primera vez descarga los datos (~24 MB) desde S3; luego tarda alrededor de 1 minuto. Ni los datos de entrada (`data/in`) ni las salidas (`data/out`, `outputs/`, `data/score`) se versionan.

> **¿Por qué los datos no están en el repo?** Git está hecho para código, no para datos: los archivos grandes hacen lento el repo y cada versión queda para siempre en el historial. Por eso los datos viven en un bucket de Amazon S3 y el pipeline los descarga cuando hacen falta.

## Flujo de trabajo del equipo (GitFlow)

| Rama | Nace de | Se integra en | Para qué |
|---|---|---|---|
| `main` | — | — | Lo que está en producción. Protegida. |
| `develop` | `main` | — | Integración del trabajo del equipo. Protegida. |
| `feature/*` | `develop` | `develop` | Nuevas funcionalidades. |
| `release/*` | `develop` | `main` y `develop` | Preparar una versión. Solo correcciones. |
| `hotfix/*` | `main` | `main` y `develop` | Urgencias en producción. |

Todo cambio a `main` o `develop` entra mediante **Pull Request** con al menos **1 aprobación**.

Laboratorio de la Sesión 3: ver [`MISIONES.md`](MISIONES.md).
