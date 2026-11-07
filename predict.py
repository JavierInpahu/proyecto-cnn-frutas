```python
import sys
import numpy as np
from PIL import Image
from tensorflow.keras.models import load_model

CLASES = [
    "Apple Golden 1",
    "Banana 1",
    "Orange 1",
    "Grape Blue 1",
    "Pineapple 1",
]

modelo = load_model("modelo_frutas.keras")

ruta_imagen = sys.argv[1] if len(sys.argv) > 1 else "imagen.jpg"

imagen = Image.open(ruta_imagen).convert("RGB")
imagen = imagen.resize((100, 100))

arreglo = np.asarray(imagen, dtype=np.float32)
entrada = np.expand_dims(arreglo, axis=0)

prediccion = modelo.predict(entrada, verbose=0)[0]

indice = int(np.argmax(prediccion))
confianza = float(prediccion[indice]) * 100

print(f"Fruta predicha: {CLASES[indice]}")
print(f"Confianza: {confianza:.2f}%")

print("\nResultados por fruta:")
for nombre, valor in zip(CLASES, prediccion):
    print(f"{nombre}: {valor * 100:.2f}%")
```
