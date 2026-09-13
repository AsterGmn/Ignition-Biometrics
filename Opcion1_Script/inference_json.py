import os
import argparse
import pickle
import json
import librosa
import soundfile as sf
import numpy as np
import torch
import nemo.collections.asr as nemo_asr
import logging

# Silenciar warnings de NeMo para que el JSON salga limpio
logging.getLogger('nemo_logger').setLevel(logging.ERROR)

def load_anti_spoofing_model(model_path):
    with open(model_path, 'rb') as f:
        clf = pickle.load(f)
    return clf

def main(audio_path, model_path="../anti_spoofing_model.pkl"):
    if not os.path.exists(audio_path):
        print(json.dumps({"error": "Archivo no encontrado"}))
        return
        
    try:
        # 1. Cargar el audio y aislar el Canal 0 (Caller / Atacante)
        y, sr = librosa.load(audio_path, sr=16000, mono=False)
        
        # Si es estéreo, librosa devuelve (2, n_samples). Tomamos el índice 0.
        if y.ndim > 1:
            y_caller = y[0, :]
        else:
            y_caller = y # Ya era mono
            
        # Guardar temporalmente el canal 0 para pasarlo a NeMo
        temp_file = "temp_caller.wav"
        sf.write(temp_file, y_caller, 16000)
        
        # 2. Análisis Acústico (TitaNet)
        speaker_model = nemo_asr.models.EncDecSpeakerLabelModel.from_pretrained(model_name="titanet_large")
        speaker_model.eval()
        
        embedding = speaker_model.get_embedding(temp_file)
        emb_np = embedding.squeeze().cpu().detach().numpy().reshape(1, -1)
        
        # 3. Predicción
        clf = load_anti_spoofing_model(model_path)
        prediction = clf.predict(emb_np)[0]
        probabilities = clf.predict_proba(emb_np)[0]
        
        # Clases: 1 = Real, 0 = Fake (IA)
        is_synthetic = bool(prediction == 0)
        confidence = float(probabilities[prediction])
        
        # 4. Generar salida JSON exacta
        output = {
            "is_synthetic": is_synthetic,
            "confidence": round(confidence, 2)
        }
        
        print(json.dumps(output, indent=2))
        
        # Limpiar
        if os.path.exists(temp_file):
            os.remove(temp_file)
            
    except Exception as e:
        print(json.dumps({"error": str(e)}))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script de inferencia - Opción 1")
    parser.add_argument("audio", help="Ruta al archivo .wav de la llamada (estéreo)")
    args = parser.parse_args()
    
    main(args.audio)
