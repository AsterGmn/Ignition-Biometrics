import os
import argparse
import pickle
import numpy as np
import nemo.collections.asr as nemo_asr
import torch

def load_anti_spoofing_model(model_path="anti_spoofing_model.pkl"):
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"No se encontró {model_path}. Entrena el modelo primero usando train_anti_spoofing.py")
    with open(model_path, 'rb') as f:
        clf = pickle.load(f)
    return clf

def main(audio_path, lang="es"):
    if not os.path.exists(audio_path):
        print(f"Error: No se encontró el archivo {audio_path}")
        return

    print("--- 1. Analizando Autenticidad del Audio (Anti-Spoofing) ---")
    # Cargar TitaNet
    print("Cargando extractor de características de voz (TitaNet)...")
    speaker_model = nemo_asr.models.EncDecSpeakerLabelModel.from_pretrained(model_name="titanet_large")
    speaker_model.eval()
    
    # Cargar el clasificador ML
    clf = load_anti_spoofing_model()
    
    # Extraer embedding
    try:
        embedding = speaker_model.get_embedding(audio_path)
        emb_np = embedding.squeeze().cpu().detach().numpy().reshape(1, -1)
        
        # Predecir
        prediction = clf.predict(emb_np)[0]
        probability = clf.predict_proba(emb_np)[0]
        
        is_real = bool(prediction == 1)
        confianza = probability[prediction] * 100
        
        if is_real:
            print(f"[RESULTADO]: El audio es GENUINO (Confianza: {confianza:.2f}%)")
        else:
            print(f"[RESULTADO]: El audio es GENERADO POR IA / FAKE (Confianza: {confianza:.2f}%)")
            print("Advertencia: Al ser detectado como IA, el reto podría rechazar esta muestra.")
            
    except Exception as e:
        print(f"Error procesando autenticidad: {e}")
        return
    
    print("\n--- 2. Transcripción de Voz (ASR) ---")
    # Elegir el modelo de lenguaje basado en 'lang'
    if lang.lower() == "es":
        # FastConformer para Español (NVIDIA NGC)
        asr_model_name = "stt_es_fastconformer_hybrid_large_pc"
    else:
        # Conformer para Inglés
        asr_model_name = "stt_en_fastconformer_hybrid_large_pc"
        
    print(f"Cargando modelo ASR ({asr_model_name})... esto puede tardar un momento...")
    try:
        asr_model = nemo_asr.models.EncDecCTCModelBPE.from_pretrained(model_name=asr_model_name)
        asr_model.eval()
        
        # Transcribir
        transcription = asr_model.transcribe([audio_path])
        print("\n--- TRANSCRIPCIÓN FINAL ---")
        print(transcription[0])
        print("---------------------------")
        
    except Exception as e:
        print(f"Error en ASR: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluar y transcribir un archivo de audio (Reto de Voz)")
    parser.add_argument("audio", help="Ruta al archivo .wav a evaluar")
    parser.add_argument("--lang", default="es", choices=["es", "en"], help="Idioma principal (es o en)")
    args = parser.parse_args()
    
    main(args.audio, args.lang)
