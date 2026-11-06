# Proyecto CNN para Clasificación de Frutas

## Objetivo

Desarrollar una Red Neuronal Convolucional (CNN) para clasificar imágenes de frutas utilizando TensorFlow y desplegar el modelo mediante una aplicación Streamlit.

## Dataset

Dataset utilizado:

Fruits-360

Clases seleccionadas:

- Apple Golden 1
- Banana 1
- Orange 1
- Grape Blue 1
- Pineapple 1

## Tecnologías Utilizadas

- Python
- TensorFlow
- Keras
- NumPy
- Pandas
- Matplotlib
- Seaborn
- Scikit-Learn
- Streamlit

## Arquitectura CNN

Entrada (100x100x3)

→ Conv2D (32)

→ MaxPooling2D

→ Conv2D (64)

→ MaxPooling2D

→ Conv2D (128)

→ MaxPooling2D

→ Flatten

→ Dense (128)

→ Dropout (0.3)

→ Dense (5)

## Resultados

- Accuracy: 100%
- Precision: 100%
- Recall: 100%
- F1-Score: 100%

## Archivos del Proyecto

- Proyecto_Final_CNN_Clasificacion_Frutas.ipynb
- train.py
- predict.py
- modelo_frutas.keras
- app.py
- requirements.txt

## Instalación

```bash
pip install -r requirements.txt
