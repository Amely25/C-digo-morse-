# -*- coding: utf-8 -*-
"""
Created on Wed May  6 18:26:58 2026

@author: Amely
"""

import os
import wave
import numpy as np
import pyaudio


# ==========================================
# CONFIGURACIÓN
# ==========================================

FORMATO = pyaudio.paInt16
CANALES = 1
TASA_MUESTREO = 44100
TAMANO_BLOQUE = 1024
TIEMPO_GRABACION = 3


# ==========================================
# FUNCIÓN PARA GRABAR AUDIO
# ==========================================

def grabar_audio():

    # --------------------------------------
    # PEDIR CARPETA Y NOMBRE
    # --------------------------------------

    carpeta = input("Escribe la carpeta donde guardarás el audio: ")
    nombre = input("Escribe el nombre del archivo: ")

    # Crear carpeta si no existe
    if not os.path.exists(carpeta):
        os.makedirs(carpeta)

    # Ruta completa
    ruta_archivo = os.path.join(carpeta, nombre + ".wav")

    # --------------------------------------
    # INICIAR AUDIO
    # --------------------------------------

    audio = pyaudio.PyAudio()

    try:

        flujo_sonido = audio.open(format=FORMATO,
                                  channels=CANALES,
                                  rate=TASA_MUESTREO,
                                  input=True,
                                  frames_per_buffer=TAMANO_BLOQUE)

        print("\nInicia la grabación...")

        fragmentos = []

        for i in range(0, int(TASA_MUESTREO / TAMANO_BLOQUE * TIEMPO_GRABACION)):

            datos_bloque = flujo_sonido.read(TAMANO_BLOQUE)

            fragmentos.append(
                np.frombuffer(datos_bloque, dtype=np.int16)
            )

        print("Termina la grabación.")

        flujo_sonido.stop_stream()
        flujo_sonido.close()

    finally:
        audio.terminate()

    # --------------------------------------
    # UNIR FRAGMENTOS
    # --------------------------------------

    senal_audio = np.hstack(fragmentos)

    # --------------------------------------
    # NORMALIZAR
    # --------------------------------------

    if np.max(np.abs(senal_audio)) != 0:

        senal_audio = (
            senal_audio / np.max(np.abs(senal_audio))
        ) * 32767

        senal_audio = senal_audio.astype(np.int16)

    # --------------------------------------
    # GUARDAR WAV
    # --------------------------------------

    archivo_wave = wave.open(ruta_archivo, "wb")

    archivo_wave.setnchannels(CANALES)

    archivo_wave.setsampwidth(
        pyaudio.PyAudio().get_sample_size(FORMATO)
    )

    archivo_wave.setframerate(TASA_MUESTREO)

    archivo_wave.writeframes(senal_audio.tobytes())

    archivo_wave.close()

    print(f"\nAudio guardado en:\n{ruta_archivo}")

    return ruta_archivo


# ==========================================
# EJECUCIÓN
# ==========================================

grabar_audio()