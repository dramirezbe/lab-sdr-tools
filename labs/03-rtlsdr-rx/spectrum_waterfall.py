#!/usr/bin/env /usr/bin/python3
"""Real-time spectrum analyzer and waterfall display using RTL-SDR via SoapySDR."""

import signal
import sys
from gnuradio import gr, qtgui
from gnuradio import soapy
from PyQt5 import Qt
import sip


class SpectrumWaterfall(gr.top_block, Qt.QWidget):
    def __init__(self, freq=100e6, gain=40, ppm=0):
        gr.top_block.__init__(self, "Spectrum Waterfall")
        Qt.QWidget.__init__(self)

        self.setWindowTitle(f"Spectrum — {freq / 1e6:.1f} MHz")
        self.setMinimumSize(900, 700)

        samp_rate = 2.4e6
        fft_size = 2048

        # RTL-SDR source
        self.src = soapy.source(
            "driver=rtlsdr",
            "fc32",
            1,
            "",
            "bufflen=16384",
            [samp_rate],
            [freq],
        )
        self.src.set_gain(0, "TUNER", gain)
        self.src.set_frequency_correction(0, ppm)

        # Frequency sink (spectrum)
        self.freq_sink = qtgui.freq_sink_c(
            fft_size,
            gr.fft.window.WIN_BLACKMAN_HARRIS,
            freq,
            samp_rate,
            "Spectrum",
        )
        self.freq_sink.set_update_time(0.05)
        self.freq_sink.set_y_axis(-120, 0)
        self.freq_sink.enable_autoscale(False)

        # Waterfall sink
        self.waterfall_sink = qtgui.waterfall_sink_c(
            fft_size,
            gr.fft.window.WIN_BLACKMAN_HARRIS,
            freq,
            samp_rate,
            "Waterfall",
        )
        self.waterfall_sink.set_update_time(0.05)
        self.waterfall_sink.set_intensity_range(-120, 0)

        # Connect
        self.connect(self.src, self.freq_sink)
        self.connect(self.src, self.waterfall_sink)

        # Layout
        layout = Qt.QVBoxLayout(self)

        freq_widget = sip.wrapinstance(self.freq_sink.qwidget(), Qt.QWidget)
        waterfall_widget = sip.wrapinstance(
            self.waterfall_sink.qwidget(), Qt.QWidget
        )

        layout.addWidget(freq_widget, 1)
        layout.addWidget(waterfall_widget, 1)

        self.show()


def main():
    freq = float(sys.argv[1]) if len(sys.argv) > 1 else 100e6
    gain = float(sys.argv[2]) if len(sys.argv) > 2 else 40
    ppm = float(sys.argv[3]) if len(sys.argv) > 3 else 0

    print(f"Spectrum Waterfall: {freq / 1e6:.1f} MHz, gain={gain} dB, ppm={ppm}")

    app = Qt.QApplication(sys.argv)
    tb = SpectrumWaterfall(freq=freq, gain=gain, ppm=ppm)

    def handler(sig, frame):
        print("\nStopping...")
        tb.stop()
        tb.wait()
        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, handler)

    tb.start()
    app.exec_()
    tb.stop()
    tb.wait()


if __name__ == "__main__":
    main()
