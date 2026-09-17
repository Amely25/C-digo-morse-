# -*- coding: utf-8 -*-
"""
Generador de código propio tipo Morse
PCR = Pelota color rojo, con sonido personalizado
"""

import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write

# =========================
# DICCIONARIO PERSONALIZADO
# =========================
# Aquí tú decides qué código corresponde a qué sonido
# "."  = punto
# "-"  = raya

CODIGO_PROPIO = {
    "PCR": ".- . . -",      # Pelota color rojo pes
    "PCV": "....-",       # Pelota color verde
    "PCA": ". .- -.",      # Pelota color azul
}

SIGNIFICADO = {
    "PCR": "Pelota color rojo",
    "PCV": "Pelota color verde",
    "PCA": "Pelota color azul",

}

# =========================
# PARÁMETROS DE AUDIO
# =========================
fs = 44100

freq_punto = 700
freq_raya = 1200

dur_punto = 0.15
dur_raya = 0.45

pausa_simbolo = 0.10
amplitud = 0.5

# =========================
# FUNCIONES
# =========================
def tono(frecuencia, duracion):
    t = np.linspace(0, duracion, int(fs * duracion), endpoint=False)
    senal = amplitud * np.sin(2 * np.pi * frecuencia * t)
    return senal


def silencio(duracion):
    return np.zeros(int(fs * duracion))


def generar_audio_codigo(codigo_usuario):
    codigo_usuario = codigo_usuario.upper()

    if codigo_usuario not in CODIGO_PROPIO:
        print("Código no encontrado.")
        return np.array([], dtype=np.float32)

    patron = CODIGO_PROPIO[codigo_usuario]
    audio = np.array([], dtype=np.float32)

    for simbolo in patron:
        if simbolo == ".":
            audio = np.concatenate((audio, tono(freq_punto, dur_punto)))

        elif simbolo == "-":
            audio = np.concatenate((audio, tono(freq_raya, dur_raya)))

        audio = np.concatenate((audio, silencio(pausa_simbolo)))

    return audio


# =========================
# PROGRAMA PRINCIPAL
# =========================
print("===================================")
print(" GENERADOR DE CÓDIGO PERSONALIZADO ")
print("===================================\n")

print("Códigos disponibles:\n")

for clave in CODIGO_PROPIO:
    print(f"{clave} = {SIGNIFICADO[clave]}  ->  patrón: {CODIGO_PROPIO[clave]}")

mensaje = input("\nEscribe el código que quieres emitir: ").upper()

if mensaje in CODIGO_PROPIO:
    print("\nCódigo seleccionado:", mensaje)
    print("Significado:", SIGNIFICADO[mensaje])
    print("Patrón sonoro:", CODIGO_PROPIO[mensaje])

    audio = generar_audio_codigo(mensaje)

    sd.play(audio, fs)
    sd.wait()

    audio_wav = np.int16(audio / np.max(np.abs(audio)) * 32767)

    nombre_archivo = f"{mensaje}_codigo.wav"
    write(nombre_archivo, fs, audio_wav)

    print("\nAudio guardado como:", nombre_archivo)

else:
    print("\nEse código no existe en tu diccionario.")
    print("Agrega el código en CODIGO_PROPIO y SIGNIFICADO.")