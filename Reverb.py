# Software Name: Reverb
# Author: Luca Bocaletto
# Description: A Python application for creating a Reverb audio effect.

import sys
import numpy as np
import sounddevice as sd
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QSlider, QLabel, QPushButton
from scipy.signal import lfilter
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# Definition of constants
SAMPLE_RATE = 44100
BLOCK_SIZE = 8192

class ReverbApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_defaults()
        self.initUI()
        self.initAudio()
        self.is_reverb_enabled = False

    def init_defaults(self):
        # Initialize default parameters
        self.reverb_gain = 0.8  # Increased reverb gain
        self.impulse_response = None
        self.reverb_length = 3000
        self.cutoff_frequency = 0.5
        self.decay_factor = 0.8
        self.audio_buffer = np.zeros(128)
        self.sliders = []

    def initUI(self):
        # Initialize the user interface
        self.setGeometry(100, 100, 400, 400)
        self.setWindowTitle('Reverb')
        self.setStyleSheet("background-color: #4B0082; color: yellow;")
        self.title_label = QLabel('Reverb')
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setFont(QFont('Arial', 24))

        self.reverb_slider = self.create_slider(self.reverb_gain, self.updateReverbGain, "Reverb Gain: {:.2f}")
        self.reverb_length_slider = self.create_slider(self.reverb_length / 10, self.updateReverbLength, "Reverb Length: {}")
        self.cutoff_frequency_slider = self.create_slider(self.cutoff_frequency, self.updateCutoffFrequency, "Cutoff Frequency: {:.2f}")
        self.decay_factor_slider = self.create_slider(self.decay_factor, self.updateDecayFactor, "Decay Factor: {:.2f}")

        self.toggle_button = QPushButton('Toggle Reverb')
        self.toggle_button.clicked.connect(self.toggleReverb)

        layout = QVBoxLayout()
        layout.addWidget(self.title_label)
        for slider, label in self.sliders:
            layout.addWidget(label)
            layout.addWidget(slider)
        layout.addWidget(self.toggle_button)
        self.setLayout(layout)

    def create_slider(self, value, callback, label_format):
        # Create and configure a slider
        slider = QSlider(orientation=1)
        slider.setRange(0, 100)
        slider.setValue(int(value * 100 if isinstance(value, float) else value))
        label = QLabel(label_format.format(value))
        slider.valueChanged.connect(callback)
        self.sliders.append((slider, label))
        return slider

    def initAudio(self):
        def audio_callback(indata, outdata, frames, time, status):
            if status:
                print("Audio status:", status, file=sys.stderr)

            if self.is_reverb_enabled and self.impulse_response is not None:
                # Apply reverb effect to the audio input
                reverb = lfilter(self.impulse_response, [1, -self.reverb_gain], indata)
                outdata[:] = reverb
            else:
                outdata[:] = indata

        self.stream = sd.Stream(
            callback=audio_callback,
            samplerate=SAMPLE_RATE,
            channels=2,
            blocksize=BLOCK_SIZE
        )

        self.stream.start()

    def updateReverbGain(self):
        # Update reverb gain based on slider input
        self.reverb_gain = self.reverb_slider.value() / 100.0
        self.sliders[0][1].setText(f"Reverb Gain: {self.reverb_gain:.2f}")

    def updateReverbLength(self):
        # Update reverb length based on slider input
        self.reverb_length = int(self.reverb_length_slider.value() * 10)
        self.updateImpulseResponse()
        self.sliders[1][1].setText(f"Reverb Length: {self.reverb_length}")

    def updateCutoffFrequency(self):
        # Update cutoff frequency based on slider input
        self.cutoff_frequency = self.cutoff_frequency_slider.value() / 100.0
        self.sliders[2][1].setText(f"Cutoff Frequency: {self.cutoff_frequency:.2f}")

    def updateDecayFactor(self):
        # Update decay factor based on slider input
        self.decay_factor = self.decay_factor_slider.value() / 100.0
        self.sliders[3][1].setText(f"Decay Factor: {self.decay_factor:.2f}")

    def updateImpulseResponse(self):
        if self.reverb_length > 0:
            # Generate a random impulse response
            self.impulse_response = np.random.randn(self.reverb_length)
            self.impulse_response = np.convolve(self.impulse_response, [1, self.decay_factor], mode='full')
            self.impulse_response /= np.max(np.abs(self.impulse_response))
        else:
            self.impulse_response = None

    def toggleReverb(self):
        # Toggle the reverb effect on/off
        self.is_reverb_enabled = not self.is_reverb_enabled

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ReverbApp()
    ex.show()
    sys.exit(app.exec_())
