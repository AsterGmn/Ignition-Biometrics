import os
import argparse
import torch
import torchaudio
from f5_tts.api import F5TTS

phrases = [
    # Verificación de identidad y seguridad
    "Hola, estoy hablando desde mi celular para confirmar mi identidad.",
    "Me pidieron que dijera esta frase de seguridad para verificar mi voz.",
    "Sí, mi fecha de nacimiento es el diez de marzo del noventa y cinco.",
    "El código de seguridad que me llegó por SMS es cuatro cinco siete.",
    "Mi nombre completo es Aster y autorizo este movimiento.",
    "Quiero desbloquear mi banca en línea, se bloqueó ayer.",
    "Me llegó un correo de que intentaron entrar a mi cuenta desde otro país.",
    "Nunca he estado en esa sucursal, ese cargo es fraude.",
    "Por favor bloqueen mi tarjeta de crédito inmediatamente, la perdí.",
    "¿Cuáles son los últimos cuatro dígitos de mi tarjeta?",
    
    # Transferencias y pagos
    "El número de cuenta al que quiero transferir es el cuatro cinco seis siete.",
    "Quiero hacer un pago de servicio de luz con mi tarjeta de crédito.",
    "¿Podrías checar el saldo de mi cuenta de ahorros, por favor?",
    "Necesito depositar veinte mil pesos a la cuenta de mi hermano.",
    "La transferencia a Juan Pérez por quinientos pesos sí la reconozco.",
    "Quiero domiciliar mi pago de internet a esta tarjeta.",
    "No ha pasado el pago de la colegiatura, ¿tienen sistema?",
    "¿Cuál es mi saldo al corte de este mes?",
    "Quiero adelantar pagos a mi crédito hipotecario.",
    "Mándame el comprobante de la transferencia a mi correo electrónico.",
    
    # Dudas generales y soporte
    "¿A qué hora cierran la sucursal del centro hoy?",
    "Quiero abrir un fondo de inversión con tasa fija.",
    "El cajero automático se tragó mi tarjeta hace diez minutos.",
    "Quiero cambiar mi número de teléfono asociado a la cuenta.",
    "Me interesa la promoción de meses sin intereses para viajes.",
    "¿Tengo puntos acumulados en mi tarjeta oro?",
    "Quiero levantar una aclaración por un cargo duplicado de Uber.",
    "Me aparece saldo retenido, ¿cuánto tarda en liberarse?",
    "Quiero solicitar un crédito automotriz, ¿qué necesito?",
    "Mi estado de cuenta no me ha llegado este mes."
]

# Duplicar y mezclar para generar volumen (llegar a 100 muestras)
phrases = (phrases * 4)[:100]

def generate_fakes():
    ref_audio = "dataset_laptop/laptop_human_ab4bd1fcb074490c919689704061c1ea.wav"
    output_dir = "audios_ia_falsos"
    
    print("Loading F5-TTS model (this may download weights)...")
    tts_engine = F5TTS()
    
    for i, target_text in enumerate(phrases):
        output_path = os.path.join(output_dir, f"f5_tts_clone_{i}.wav")
        print(f"Synthesizing [{i+1}/10]: '{target_text}'")
        
        # F5-TTS handles ref_text="" automatically by transcribing with Whisper if needed
        wav_np, sample_rate, _ = tts_engine.infer(
            ref_file=ref_audio,
            ref_text="",
            gen_text=target_text
        )
        
        wav_tensor = torch.from_numpy(wav_np).unsqueeze(0)
        torchaudio.save(output_path, wav_tensor, sample_rate)
        print(f"Audio generated successfully: {output_path}")

if __name__ == "__main__":
    generate_fakes()
