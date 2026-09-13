import os
import argparse
import pickle
import numpy as np
import torch
import nemo.collections.asr as nemo_asr

def main(audio_path, user_name, db_path="speaker_database.pkl"):
    if not os.path.exists(audio_path):
        print(f"Error: No se encontró el archivo de audio {audio_path}")
        return

    print("Cargando extractor de características de voz (TitaNet)...")
    speaker_model = nemo_asr.models.EncDecSpeakerLabelModel.from_pretrained(model_name="titanet_large")
    speaker_model.eval()

    print(f"Extrayendo huella vocal para el usuario: {user_name}...")
    try:
        embedding = speaker_model.get_embedding(audio_path)
        emb_np = embedding.squeeze().cpu().detach().numpy()
        
        # Cargar base de datos existente o crear una nueva
        if os.path.exists(db_path):
            with open(db_path, 'rb') as f:
                speaker_db = pickle.load(f)
        else:
            speaker_db = {}
            
        # Guardar la huella vocal del usuario
        speaker_db[user_name] = emb_np
        
        with open(db_path, 'wb') as f:
            pickle.dump(speaker_db, f)
            
        print(f"¡Éxito! El usuario '{user_name}' ha sido registrado en la base de datos de voces.")
        
    except Exception as e:
        print(f"Error procesando el registro: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Registrar la huella vocal de un usuario")
    parser.add_argument("audio", help="Ruta al archivo .wav real del usuario")
    parser.add_argument("name", help="Nombre del usuario a registrar")
    args = parser.parse_args()
    
    main(args.audio, args.name)
