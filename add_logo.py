import codecs

with open(r'C:\Users\Aster\Documents\RetoVoz\logo_b64.txt', 'r') as f:
    b64_img = f.read()

with codecs.open("api.py", "r", encoding="utf-8") as f:
    content = f.read()

# Add CSS
css_addition = """
            .corner-logo { position: absolute; top: 20px; right: 20px; width: 80px; height: auto; border-radius: 50%; box-shadow: 0 0 15px rgba(187, 134, 252, 0.4); transition: transform 0.3s ease; }
            .corner-logo:hover { transform: scale(1.1); }
            .footer { margin-top: 30px; font-size: 12px; color: #666; letter-spacing: 1px; text-transform: uppercase; }
"""
content = content.replace("</style>", css_addition + "\n        </style>")

# Add Logo Image to body
logo_html = f'<img src="data:image/jpeg;base64,{b64_img}" class="corner-logo" alt="V8 Coders Logo">'
content = content.replace("<body>", "<body>\n        " + logo_html)

# Add Footer to container
footer_html = '<div class="footer">Developed by V8 Coders</div>\n        </div>'
content = content.replace("</div>\n\n        <script>", footer_html + "\n\n        <script>")

with codecs.open("api.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Logo and footer added successfully.")
