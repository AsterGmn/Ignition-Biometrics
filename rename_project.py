import codecs

with codecs.open("api.py", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("<h1>Sistema Anti-Spoofing Corporativo</h1>", "<h1>VocalGuard AI</h1>")
content = content.replace("<title>Reto Voz - Detección Anti-Spoofing</title>", "<title>VocalGuard AI - V8 Coders</title>")

with codecs.open("api.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Title updated to VocalGuard AI.")
