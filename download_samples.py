import urllib.request
import os

def download_audio(url, filepath):
    try:
        urllib.request.urlretrieve(url, filepath)
        print(f"Descargado: {filepath}")
    except Exception as e:
        print(f"Error descargando {filepath}: {e}")

# Crear carpetas si no existen
os.makedirs("dataset/real", exist_ok=True)
os.makedirs("dataset/fake", exist_ok=True)

# Descargar audios de muestra "Reales" (Grabaciones de voz públicas de Microsoft/Google)
real_urls = [
    "https://raw.githubusercontent.com/microsoft/Cognitive-CustomTTS-Sample-Data/main/Sample-Data/Audio/0001.wav",
    "https://raw.githubusercontent.com/microsoft/Cognitive-CustomTTS-Sample-Data/main/Sample-Data/Audio/0002.wav",
    "https://raw.githubusercontent.com/microsoft/Cognitive-CustomTTS-Sample-Data/main/Sample-Data/Audio/0003.wav",
    "https://raw.githubusercontent.com/microsoft/Cognitive-CustomTTS-Sample-Data/main/Sample-Data/Audio/0004.wav"
]

# Descargar audios de muestra "Fakes / IA" (Usamos otros audios de muestra públicos para simular la IA)
fake_urls = [
    "https://raw.githubusercontent.com/microsoft/Cognitive-CustomTTS-Sample-Data/main/Sample-Data/Audio/0005.wav",
    "https://raw.githubusercontent.com/microsoft/Cognitive-CustomTTS-Sample-Data/main/Sample-Data/Audio/0006.wav",
    "https://raw.githubusercontent.com/microsoft/Cognitive-CustomTTS-Sample-Data/main/Sample-Data/Audio/0007.wav",
    "https://raw.githubusercontent.com/microsoft/Cognitive-CustomTTS-Sample-Data/main/Sample-Data/Audio/0008.wav"
]

print("Descargando muestras reales...")
for i, url in enumerate(real_urls):
    download_audio(url, f"dataset/real/muestra_humana_{i+1}.wav")

print("Descargando muestras sintéticas (IA)...")
for i, url in enumerate(fake_urls):
    download_audio(url, f"dataset/fake/muestra_ia_{i+1}.wav")

print("¡Descarga de muestras finalizada!")
