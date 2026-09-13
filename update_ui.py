import re

with open("api.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add /detect_stream endpoint
if "@app.post(\"/detect_stream\")" not in content:
    stream_endpoint = """
@app.post("/detect_stream")
async def detect_stream(file: UploadFile = File(...)):
    import tempfile, os, librosa, numpy as np, soundfile as sf
    temp_input = tempfile.mktemp(suffix=".webm")
    temp_mono = tempfile.mktemp(suffix=".wav")
    try:
        with open(temp_input, "wb") as f:
            f.write(await file.read())
        
        y, sr = librosa.load(temp_input, sr=16000, mono=False)
        if y.ndim > 1: y_caller = y[0, :]
        else: y_caller = y
        
        sf.write(temp_mono, y_caller, 16000)
        
        features = feature_extractor([temp_mono])[0]
        feats_reshaped = features.unsqueeze(0).unsqueeze(0)
        
        with torch.no_grad():
            embeddings = embedding_model(audio_signal=feats_reshaped, length=torch.tensor([feats_reshaped.shape[-1]]))
        
        emb_np = embeddings[0].cpu().numpy().reshape(1, -1)
        pred = model.predict(emb_np)[0]
        prob = model.predict_proba(emb_np)[0]
        
        is_synthetic = bool(pred == 0)
        confidence = float(prob[0] if is_synthetic else prob[1])
        
        return {"is_synthetic": is_synthetic, "confidence": confidence}
    except Exception as e:
        return {"error": str(e)}
    finally:
        if os.path.exists(temp_input): os.remove(temp_input)
        if os.path.exists(temp_mono): os.remove(temp_mono)

"""
    content = content.replace("@app.get(\"/\", response_class=HTMLResponse)", stream_endpoint + "@app.get(\"/\", response_class=HTMLResponse)")


# 2. Update the frontend UI with stream capabilities
css_addition = """
            .stream-btn { background-color: #ff9900; color: #000; margin-top: 15px; }
            .stream-btn:hover { background-color: #cc7a00; }
            .bars-container { display: none; margin-top: 20px; text-align: left; background: #111; padding: 15px; border-radius: 8px; border: 1px solid #333; }
            .bar-row { margin-bottom: 10px; }
            .bar-label { display: flex; justify-content: space-between; margin-bottom: 5px; font-weight: bold; font-size: 14px; }
            .bar-bg { width: 100%; height: 20px; background: #333; border-radius: 10px; overflow: hidden; }
            .bar-fill { height: 100%; width: 0%; transition: width 0.3s ease; }
            .fill-human { background: linear-gradient(90deg, #004d00, #00ff00); }
            .fill-ai { background: linear-gradient(90deg, #4d0000, #ff3333); }
"""
content = content.replace(".divider { margin: 20px 0; border-bottom: 1px solid #333; }", ".divider { margin: 20px 0; border-bottom: 1px solid #333; }" + css_addition)

html_addition = """
            <button id="stream-btn" class="upload-btn stream-btn">🎙️ Análisis en Tiempo Real (Stream)</button>
            
            <div id="bars-container" class="bars-container">
                <div style="text-align: center; color: #ff9900; margin-bottom: 15px; font-weight: bold; font-size: 14px; animation: blinker 1s linear infinite;">🔴 Analizando flujo de audio en vivo...</div>
                
                <div class="bar-row">
                    <div class="bar-label">
                        <span style="color: #00ff00;">Probabilidad Humano</span>
                        <span id="human-pct" style="color: #00ff00;">0%</span>
                    </div>
                    <div class="bar-bg">
                        <div id="human-bar" class="bar-fill fill-human"></div>
                    </div>
                </div>

                <div class="bar-row">
                    <div class="bar-label">
                        <span style="color: #ff3333;">Probabilidad IA (Deepfake)</span>
                        <span id="ai-pct" style="color: #ff3333;">0%</span>
                    </div>
                    <div class="bar-bg">
                        <div id="ai-bar" class="bar-fill fill-ai"></div>
                    </div>
                </div>
            </div>
"""
content = content.replace('<button id="record-btn"', html_addition + '\n            <button id="record-btn"')

js_addition = """
            let streamInterval;
            let streamMediaRecorder;
            let isStreaming = false;
            const streamBtn = document.getElementById('stream-btn');
            const barsContainer = document.getElementById('bars-container');
            const humanBar = document.getElementById('human-bar');
            const aiBar = document.getElementById('ai-bar');
            const humanPct = document.getElementById('human-pct');
            const aiPct = document.getElementById('ai-pct');

            streamBtn.addEventListener('click', async () => {
                if (isStreaming) {
                    isStreaming = false;
                    clearInterval(streamInterval);
                    streamBtn.innerHTML = '🎙️ Análisis en Tiempo Real (Stream)';
                    barsContainer.style.display = 'none';
                    return;
                }

                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    isStreaming = true;
                    streamBtn.innerHTML = '⏹️ Detener Análisis en Vivo';
                    barsContainer.style.display = 'block';
                    document.getElementById('result').style.display = 'none';
                    document.getElementById('spectrogram-img').style.display = 'none';
                    
                    // Reset bars
                    humanBar.style.width = '0%'; aiBar.style.width = '0%';
                    humanPct.innerText = '0%'; aiPct.innerText = '0%';

                    // Capturar fragmentos de 1.5s continuamente
                    streamInterval = setInterval(async () => {
                        let mr = new MediaRecorder(stream);
                        let chunks = [];
                        mr.ondataavailable = e => chunks.push(e.data);
                        mr.onstop = async () => {
                            if (!isStreaming) return;
                            let blob = new Blob(chunks, { type: 'audio/webm' });
                            let formData = new FormData();
                            formData.append("file", new File([blob], "chunk.webm", {type: 'audio/webm'}));
                            
                            try {
                                let res = await fetch('/detect_stream', {method: 'POST', body: formData});
                                let data = await res.json();
                                if(!data.error) {
                                    let fakeConf = data.is_synthetic ? data.confidence * 100 : (1 - data.confidence) * 100;
                                    let humanConf = 100 - fakeConf;
                                    
                                    humanBar.style.width = humanConf.toFixed(1) + '%';
                                    humanPct.innerText = humanConf.toFixed(1) + '%';
                                    
                                    aiBar.style.width = fakeConf.toFixed(1) + '%';
                                    aiPct.innerText = fakeConf.toFixed(1) + '%';
                                }
                            } catch(e) {}
                        };
                        mr.start();
                        setTimeout(() => {
                            if(mr.state === "recording") mr.stop();
                        }, 1500); // 1.5 seconds chunk
                    }, 1600); // repeat every 1.6s

                } catch (err) {
                    alert("No se pudo acceder al micrófono.");
                }
            });
"""
content = content.replace("let mediaRecorder;", js_addition + "\n            let mediaRecorder;")

with open("api.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Updated api.py successfully.")
