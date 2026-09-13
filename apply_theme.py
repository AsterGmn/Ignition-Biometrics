import codecs

with codecs.open("api.py", "r", encoding="utf-8") as f:
    content = f.read()

# CSS changes for purple/black theme and larger fonts
css_replacements = {
    # Increase base font size by roughly 2-4px (using larger percentages or em/px)
    "body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #121212; color: #ffffff; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; margin: 0; padding: 20px; }": 
    "body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0a0a0a; color: #f0f0f0; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; margin: 0; padding: 20px; font-size: 18px; }",
    
    # Title color from cyan to purple, larger
    "h1 { color: #00e5ff; font-size: 24px; margin-bottom: 10px; }": 
    "h1 { color: #bb86fc; font-size: 28px; margin-bottom: 10px; font-weight: 600; }",
    
    # Subtitle larger
    "<p style=\"color: #aaa; font-size: 14px; margin-bottom: 20px;\">": 
    "<p style=\"color: #bbb; font-size: 16px; margin-bottom: 25px;\">",
    
    # Container simplified, faint purple glow
    ".container { background-color: #1e1e1e; padding: 30px; border-radius: 12px; box-shadow: 0 8px 32px rgba(0, 229, 255, 0.1); text-align: center; width: 500px; max-width: 90%; }": 
    ".container { background-color: #121212; padding: 35px; border-radius: 8px; box-shadow: 0 4px 20px rgba(187, 134, 252, 0.15); text-align: center; width: 550px; max-width: 95%; border: 1px solid #2a2a2a; }",
    
    # Buttons to purple
    ".upload-btn { background-color: #00e5ff; color: #000; padding: 14px 24px; border: none; border-radius: 6px; font-size: 16px; font-weight: bold; cursor: pointer; margin-top: 10px; width: 100%; transition: 0.3s; }":
    ".upload-btn { background-color: #bb86fc; color: #000; padding: 16px 24px; border: none; border-radius: 4px; font-size: 18px; font-weight: bold; cursor: pointer; margin-top: 10px; width: 100%; transition: 0.2s; }",
    
    ".upload-btn:hover { background-color: #00b3cc; transform: scale(1.02); }":
    ".upload-btn:hover { background-color: #9c27b0; color: #fff; transform: translateY(-2px); }",
    
    # Override specific colored buttons to fit the purple/black theme
    ".record-btn { background-color: #ff3366; color: #fff; margin-top: 15px; }":
    ".record-btn { background-color: #3700b3; color: #fff; margin-top: 15px; }",
    
    ".record-btn:hover { background-color: #cc0033; }":
    ".record-btn:hover { background-color: #6200ee; }",
    
    ".stream-btn { background-color: #ff9900; color: #000; margin-top: 15px; }":
    ".stream-btn { background-color: #03dac6; color: #000; margin-top: 15px; }",
    
    ".stream-btn:hover { background-color: #cc7a00; }":
    ".stream-btn:hover { background-color: #018786; color: #fff; }",
    
    ".train-btn { background-color: #00ff00; color: #000; margin-top: 15px; display: none; }":
    ".train-btn { background-color: #cf6679; color: #000; margin-top: 15px; display: none; }",
    
    ".train-btn:hover { background-color: #00cc00; }":
    ".train-btn:hover { background-color: #b33951; color: #fff; }",
    
    # File Drop Area
    ".file-label { display: block; border: 2px dashed #00e5ff; padding: 20px; border-radius: 8px; cursor: pointer; color: #aaa; margin-bottom: 10px; transition: 0.3s; }":
    ".file-label { display: block; border: 2px dashed #bb86fc; padding: 25px; border-radius: 4px; cursor: pointer; color: #ccc; margin-bottom: 15px; transition: 0.2s; font-size: 18px; }",
    
    ".file-label:hover { background-color: #2a2a2a; color: #fff; border-color: #fff; }":
    ".file-label:hover { background-color: #1e1e1e; color: #fff; border-color: #bb86fc; }",
    
    # Loader
    "#loader { display: none; margin-top: 20px; color: #00e5ff; font-style: italic; }":
    "#loader { display: none; margin-top: 20px; color: #bb86fc; font-size: 16px; letter-spacing: 1px; }",
    
    # Result font sizes
    "#result { margin-top: 20px; padding: 15px; border-radius: 8px; display: none; font-size: 18px; font-weight: bold; line-height: 1.5; }":
    "#result { margin-top: 20px; padding: 20px; border-radius: 4px; display: none; font-size: 20px; font-weight: normal; line-height: 1.6; }",
    
    # Drop Text
    "<span style=\"font-size: 12px; color: #666;\">(.wav)</span>":
    "<span style=\"font-size: 14px; color: #888;\">(.wav)</span>",
    
    "<span style=\"font-size: 14px; color: #00e5ff; font-weight: bold;\">":
    "<span style=\"font-size: 16px; color: #bb86fc; font-weight: bold;\">",
    
    "document.getElementById('drop-area').style.borderColor = \"#00ff00\";":
    "document.getElementById('drop-area').style.borderColor = \"#bb86fc\";"
}

for old, new in css_replacements.items():
    content = content.replace(old, new)

with codecs.open("api.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Theme updated to purple/black, simplified design, larger fonts.")
