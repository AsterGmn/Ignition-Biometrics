import re
import codecs

with codecs.open("api.py", "r", encoding="utf-8") as f:
    content = f.read()

# Replace specific texts
replacements = {
    "🤖 Motor Anti-Spoofing": "Sistema Anti-Spoofing Corporativo",
    "🤖": "",
    "🎙️ Análisis en Tiempo Real (Stream)": "Análisis en Tiempo Real (Stream)",
    "🎙️": "",
    "Probabilidad IA (Deepfake)": "Probabilidad de Anomalía Sintética",
    "💾 Guardar mi voz para Entrenar la IA": "Guardar Muestra en BD Biométrica",
    "💾": "",
    "📁 Subir archivo de audio": "Subir archivo de audio",
    "📁": "",
    "✅ Archivo Listo": "Archivo Listo",
    "✅": "",
    "✅ AUTENTICACIÓN EXITOSA ✅": "AUTENTICACIÓN EXITOSA",
    "🚨 ¡ALERTA DE FRAUDE! 🚨": "¡ALERTA DE FRAUDE!",
    "🚨": "",
    "⏹️ Detener Análisis en Vivo": "Detener Análisis en Vivo",
    "⏹️": "",
    "🔴 Analizando flujo de audio en vivo...": "Analizando flujo de audio en vivo...",
    "🔴": "",
    "🧠": "",
    "📈": ""
}

for old, new in replacements.items():
    content = content.replace(old, new)

# We can also strip any remaining emojis using a regex, but the dict covers the ones we added.

with codecs.open("api.py", "w", encoding="utf-8") as f:
    f.write(content)

print("UI sanitized and made professional.")
