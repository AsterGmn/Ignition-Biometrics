import os
import argparse
import pickle
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import torch
import nemo.collections.asr as nemo_asr

def load_anti_spoofing_model(model_path="anti_spoofing_model.pkl"):
    with open(model_path, 'rb') as f:
        clf = pickle.load(f)
    return clf

def main(audio_path, threshold=0.75):
    if not os.path.exists(audio_path):
        print(f"Error: Archivo no encontrado {audio_path}")
        return

    print("--- FASE 1: Detección de Anti-Spoofing (Deepfake) ---")
    speaker_model = nemo_asr.models.EncDecSpeakerLabelModel.from_pretrained(model_name="titanet_large")
    speaker_model.eval()

    embedding = speaker_model.get_embedding(audio_path)
    emb_np = embedding.squeeze().cpu().detach().numpy()
    
    try:
        clf = load_anti_spoofing_model()
        prediction = clf.predict(emb_np.reshape(1, -1))[0]
        if prediction == 0:
            print("[ALERTA DE SEGURIDAD]: Se detectó que este audio fue GENERADO POR IA.")
            print("Acceso DENEGADO.")
            return
        else:
            print("[OK] Audio genuino detectado. Procediendo a autenticación...")
    except FileNotFoundError:
        print("Advertencia: No se encontró anti_spoofing_model.pkl. Saltando validación de IA...")

    print("\n--- FASE 2: Autenticación Biométrica (Reconocimiento del Hablante) ---")
    db_path = "speaker_database.pkl"
    if not os.path.exists(db_path):
        print("Error: No hay usuarios registrados. Usa enroll_user.py primero.")
        return
        
    with open(db_path, 'rb') as f:
        speaker_db = pickle.load(f)
        
    best_match = None
    highest_similarity = -1.0
    
    for user_name, saved_emb in speaker_db.items():
        # Calcular similitud coseno entre el audio de entrada y los usuarios registrados
        sim = cosine_similarity(emb_np.reshape(1, -1), saved_emb.reshape(1, -1))[0][0]
        if sim > highest_similarity:
            highest_similarity = sim
            best_match = user_name
            
    if highest_similarity >= threshold:
        print(f"[ACCESO CONCEDIDO] Bienvenido {best_match} (Nivel de confianza: {highest_similarity*100:.2f}%)")
    else:
        print(f"[ACCESO DENEGADO] No se reconoció la voz. Mayor similitud fue {highest_similarity*100:.2f}% (Se requiere {threshold*100:.2f}%)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Autenticar usuario por voz (Anti-IA + Biometría)")
    parser.add_argument("audio", help="Ruta al archivo .wav a autenticar")
    parser.add_argument("--threshold", type=float, default=0.75, help="Umbral de similitud (ej. 0.75)")
    args = parser.parse_args()
    
    main(args.audio, args.threshold)
