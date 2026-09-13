# HackMTY26 - Defend the Bank Against Voice Deepfakes

## Equipo: [Tu Nombre de Equipo]

### Approach (Enfoque)
Nuestra solución aborda el reto mediante **Acoustic Detection** (Detección Acústica) combinando redes neuronales profundas y técnicas de *Data Augmentation* para combatir el "Domain Mismatch".

**Modelo Base:** 
Utilizamos **TitaNet** (NVIDIA NeMo), un modelo *State-of-the-Art* diseñado específicamente para extraer características biométricas del espectro de voz (Embeddings), el cual alimenta un clasificador estadístico (Regresión Logística).

**Innovaciones Clave:**
1. **Dynamic Chunking:** El pipeline no analiza toda la llamada de golpe. Corta el audio en fragmentos de 4 segundos, extrae el *embedding* de cada bloque y promedia los resultados. Esto hace al sistema increíblemente robusto frente a llamadas de duraciones variables (desde 5 segundos hasta 4 minutos) y evita Timeouts (Latencia Promedio: ~1.2s).
2. **Domain Mismatch Correction & Adversarial Training:** Para evitar que la IA confunda "Audio Limpio" con "Voz Humana", inyectamos grabaciones humanas de alta definición y aplicamos **Entrenamiento Adversario** utilizando **F5-TTS** (modelo Zero-Shot State-of-the-Art) para generar ataques de voz ultra-realistas.
3. **Telephony Noise Augmentation:** Se implementó una capa matemática de inyección de ruido blanco en el pipeline de entrenamiento para corromper dinámicamente audios limpios, forzando a la red neuronal a evaluar puramente el timbre biométrico y no los canales de grabación.
4. **API Base64 Ready:** El endpoint `/detect` parsea robustamente JSONs con la llave `audio_base64`, cumpliendo estrictamente con el contrato del reto, y cuenta con una interfaz gráfica en `/` para demostraciones en vivo.

### Instrucciones de Ejecución

**Requisitos:** Docker Desktop instalado.

1. Construir la imagen de Docker (Solo la primera vez):
   `docker build -t reto-voz-env .`

2. Levantar el entorno y mapear los puertos:
   `docker run --rm -p 8080:8000 -v "${PWD}:/workspace" reto-voz-env bash`

3. Iniciar la API:
   `python api.py`

4. Probar:
   - Evaluador Oficial (Base64): Enviar petición POST a `http://localhost:8080/detect`
   - Interfaz Gráfica Interactiva: Abrir `http://localhost:8080/` en el navegador web.

---
*Desarrollado para el Challenge Track de Altur.*
