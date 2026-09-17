# -*- coding: utf-8 -*-

import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
from scipy.signal import firwin, filtfilt
from scipy.ndimage import uniform_filter1d

# =========================
# DICCIONARIO
# =========================
CODIGO_PROPIO = {
    "PCR": ".-..-",
    "PCV": "....-",
    "PCA": "..--.",
}

SIGNIFICADO = {
    "PCR": "Pelota color rojo",
    "PCV": "Pelota color verde",
    "PCA": "Pelota color azul",
}

# =========================
# AUDIO
# =========================
fs = 44100
DURACION_ESCUCHA = 6

freq_punto = 697
freq_raya = 1195

# =========================
# FILTRO
# =========================
tolerancia = 5
numtaps = 4001

# =========================
# DETECCIÓN POR ENVOLVENTE
# =========================
UMBRAL_REL = 0.25        # sube a 0.30 si detecta ruido
VENTANA_ENV = 800        # suavizado de envolvente
MIN_TONO = 0.08          # duración mínima de símbolo
MIN_SILENCIO = 0.035     # pausa mínima para separar símbolos

# =========================
# FUNCIONES
# =========================
def normalizar(x):
    return x / (np.max(np.abs(x)) + 1e-12)

def filtro_fir_pasabandas(audio, f_central):
    f1 = f_central - tolerancia
    f2 = f_central + tolerancia

    h = firwin(
        numtaps,
        [f1, f2],
        pass_zero=False,
        fs=fs,
        window="blackman"
    )

    return filtfilt(h, [1.0], audio)

def detectar_patron(audio):
    y697 = filtro_fir_pasabandas(audio, freq_punto)
    y1195 = filtro_fir_pasabandas(audio, freq_raya)

    env697 = uniform_filter1d(np.abs(y697), size=VENTANA_ENV)
    env1195 = uniform_filter1d(np.abs(y1195), size=VENTANA_ENV)

    th697 = UMBRAL_REL * np.max(env697)
    th1195 = UMBRAL_REL * np.max(env1195)

    etiquetas = []

    for e697, e1195 in zip(env697, env1195):

        if e697 > th697 and e697 > e1195:
            etiquetas.append(".")
        elif e1195 > th1195 and e1195 > e697:
            etiquetas.append("-")
        else:
            etiquetas.append(" ")

    # =========================
    # AGRUPAR SEGMENTOS
    # =========================
    patron = ""
    segmentos = []

    actual = etiquetas[0]
    inicio = 0

    for i in range(1, len(etiquetas)):
        if etiquetas[i] != actual:
            dur = (i - inicio) / fs

            if actual in [".", "-"] and dur >= MIN_TONO:
                patron += actual
                segmentos.append((actual, dur))

            actual = etiquetas[i]
            inicio = i

    dur = (len(etiquetas) - inicio) / fs
    if actual in [".", "-"] and dur >= MIN_TONO:
        patron += actual
        segmentos.append((actual, dur))

    return patron, segmentos, y697, y1195, env697, env1195

# =========================
# PROGRAMA PRINCIPAL
# =========================
print("=" * 50)
print(" RECEPTOR MORSE CON FIR + ENVOLVENTE")
print("=" * 50)

for clave, patron in CODIGO_PROPIO.items():
    print(f"{clave} -> {patron}")

while True:
    input("\nPresiona ENTER para escuchar...")

    print(f"\nGrabando {DURACION_ESCUCHA} s...\n")

    audio_grabado = sd.rec(
        int(fs * DURACION_ESCUCHA),
        samplerate=fs,
        channels=1,
        dtype="float32"
    )
    sd.wait()

    audio = audio_grabado[:, 0]
    audio = audio - np.mean(audio)
    audio = normalizar(audio)

    patron, segmentos, y697, y1195, env697, env1195 = detectar_patron(audio)

    print(f"\nSegmentos detectados: {segmentos}")
    print(f"Patrón detectado: {patron}")

    encontrado = False

    for clave, ref in CODIGO_PROPIO.items():
        if patron == ref:
            print("\n" + "=" * 50)
            print(f"CÓDIGO IDENTIFICADO : {clave}")
            print(f"SIGNIFICADO         : {SIGNIFICADO[clave]}")
            print("=" * 50)
            encontrado = True
            break

    if not encontrado:
        print("\nPatrón no reconocido.")
        print("Esperados:")
        for clave, ref in CODIGO_PROPIO.items():
            print(f"{clave}: {ref}")

    ver = input("\n¿Ver gráfica? (s/n): ").strip().lower()

    if ver == "s":
        t = np.arange(len(audio)) / fs

        plt.figure(figsize=(12, 8))

        plt.subplot(3, 1, 1)
        plt.plot(t, audio)
        plt.title("Audio original")
        plt.grid()

        plt.subplot(3, 1, 2)
        plt.plot(t, env697)
        plt.title("Envolvente 697 Hz")
        plt.grid()

        plt.subplot(3, 1, 3)
        plt.plot(t, env1195)
        plt.title("Envolvente 1195 Hz")
        plt.xlabel("Tiempo [s]")
        plt.grid()

        plt.tight_layout()
        plt.show()

    otra = input("\n¿Escuchar otra vez? (s/n): ").strip().lower()

    if otra != "s":
        print("\nReceptor cerrado.")
        break