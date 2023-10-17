# Nome del Software: Reverb
# Autore: Luca Bocaletto
# Descrizione: Applicazione Python per creare un effetto audio Reverb.

import sys
import numpy as np
import sounddevice as sd
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QSlider, QLabel, QPushButton
from scipy.signal import lfilter
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# Definizione delle costanti
FREQUENZA_CAMPIONAMENTO = 44100
DIMENSIONE_BLOCCO = 8192

class AppReverb(QWidget):
    def __init__(self):
        super().__init__()
        self.inizializza_predefiniti()
        self.inizializza_UI()
        self.inizializza_Audio()
        self.reverb_attivo = False

    def inizializza_predefiniti(self):
        # Inizializza i parametri predefiniti
        self.gain_reverb = 0.8  # Aumento del guadagno del riverbero
        self.risposta_impulso = None
        self.lunghezza_reverb = 3000
        self.frequenza_di_taglio = 0.5
        self.fattore_decay = 0.8
        self.buffer_audio = np.zeros(128)
        self.slider = []

    def inizializza_UI(self):
        # Inizializza l'interfaccia utente
        self.setGeometry(100, 100, 400, 400)
        self.setWindowTitle('Reverbero')
        self.setStyleSheet("background-color: #4B0082; color: yellow;")
        self.label_titolo = QLabel('Reverbero')
        self.label_titolo.setAlignment(Qt.AlignCenter)
        self.label_titolo.setFont(QFont('Arial', 24))

        self.slider_reverb = self.crea_slider(self.gain_reverb, self.aggiorna_guadagno_reverb, "Guadagno Reverbero: {:.2f}")
        self.slider_lunghezza_reverb = self.crea_slider(self.lunghezza_reverb / 10, self.aggiorna_lunghezza_reverb, "Lunghezza Reverbero: {}")
        self.slider_frequenza_di_taglio = self.crea_slider(self.frequenza_di_taglio, self.aggiorna_frequenza_di_taglio, "Frequenza di Taglio: {:.2f}")
        self.slider_fattore_decay = self.crea_slider(self.fattore_decay, self.aggiorna_fattore_decay, "Fattore di Decay: {:.2f}")

        self.pulsante_toggle = QPushButton('Attiva/Disattiva Reverbero')
        self.pulsante_toggle.clicked.connect(self.cambia_stato_reverb)

        layout = QVBoxLayout()
        layout.addWidget(self.label_titolo)
        for slider, label in self.slider:
            layout.addWidget(label)
            layout.addWidget(slider)
        layout.addWidget(self.pulsante_toggle)
        self.setLayout(layout)

    def crea_slider(self, valore, callback, formato_label):
        # Crea e configura uno slider
        slider = QSlider(orientation=1)
        slider.setRange(0, 100)
        slider.setValue(int(valore * 100) if isinstance(valore, float) else valore)
        label = QLabel(formato_label.format(valore))
        slider.valueChanged.connect(callback)
        self.slider.append((slider, label))
        return slider

    def inizializza_Audio(self):
        def callback_audio(indata, outdata, frames, time, status):
            if status:
                print("Stato Audio:", status, file=sys.stderr)

            if self.reverb_attivo and self.risposta_impulso is not None:
                # Applica l'effetto di riverbero all'input audio
                riverbero = lfilter(self.risposta_impulso, [1, -self.gain_reverb], indata)
                outdata[:] = riverbero
            else:
                outdata[:] = indata

        self.stream = sd.Stream(
            callback=callback_audio,
            samplerate=FREQUENZA_CAMPIONAMENTO,
            channels=2,
            blocksize=DIMENSIONE_BLOCCO
        )

        self.stream.start()

    def aggiorna_guadagno_reverb(self):
        # Aggiorna il guadagno del riverbero in base all'input dello slider
        self.gain_reverb = self.slider_reverb.value() / 100.0
        self.slider[0][1].setText(f"Guadagno Reverbero: {self.gain_reverb:.2f}")

    def aggiorna_lunghezza_reverb(self):
        # Aggiorna la lunghezza del riverbero in base all'input dello slider
        self.lunghezza_reverb = int(self.slider_lunghezza_reverb.value() * 10)
        self.aggiorna_risposta_impulso()
        self.slider[1][1].setText(f"Lunghezza Reverbero: {self.lunghezza_reverb}")

    def aggiorna_frequenza_di_taglio(self):
        # Aggiorna la frequenza di taglio in base all'input dello slider
        self.frequenza_di_taglio = self.slider_frequenza_di_taglio.value() / 100.0
        self.slider[2][1].setText(f"Frequenza di Taglio: {self.frequenza_di_taglio:.2f}")

    def aggiorna_fattore_decay(self):
        # Aggiorna il fattore di decay in base all'input dello slider
        self.fattore_decay = self.slider_fattore_decay.value() / 100.0
        self.slider[3][1].setText(f"Fattore di Decay: {self.fattore_decay:.2f}")

    def aggiorna_risposta_impulso(self):
        if self.lunghezza_reverb > 0:
            # Genera una risposta all'impulso casuale
            self.risposta_impulso = np.random.randn(self.lunghezza_reverb)
            self.risposta_impulso = np.convolve(self.risposta_impulso, [1, self.fattore_decay], mode='full')
            self.risposta_impulso /= np.max(np.abs(self.risposta_impulso))
        else:
            self.risposta_impulso = None

    def cambia_stato_reverb(self):
        # Attiva/Disattiva l'effetto di riverbero
        self.reverb_attivo = not self.reverb_attivo

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = AppReverb()
    ex.show()
    sys.exit(app.exec_())
