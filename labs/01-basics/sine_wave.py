#!/usr/bin/env python3
"""Simplest GNU Radio example: sine wave → time sink + FFT sink."""

from gnuradio import gr, analog, blocks, qtgui
from PyQt5 import Qt
import sys
import sip


class SineWaveFlowgraph(gr.top_block, Qt.QWidget):
    def __init__(self):
        gr.top_block.__init__(self, "Sine Wave Example")
        Qt.QWidget.__init__(self)

        self.setWindowTitle("Sine Wave Example")

        samp_rate = 32000
        freq = 1000

        self.source = analog.sig_source_f(samp_rate, analog.GR_SIN_WAVE, freq, 1, 0)
        self.throttle = blocks.throttle(gr.sizeof_float, samp_rate, True)

        self.time_sink = qtgui.time_sink_f(1024, samp_rate, "Time", 1)
        self.time_sink.set_y_axis(-1.5, 1.5)

        self.freq_sink = qtgui.freq_sink_f(1024, qtgui.window.WIN_BLACKMAN_hARRIS, 0, samp_rate, "Frequency")

        self.connect(self.source, self.throttle)
        self.connect(self.throttle, self.time_sink)
        self.connect(self.throttle, self.freq_sink)

        layout = Qt.QVBoxLayout(self)
        layout.addWidget(sip.wrapinstance(self.time_sink.qwidget(), Qt.QWidget))
        layout.addWidget(sip.wrapinstance(self.freq_sink.qwidget(), Qt.QWidget))


def main():
    qapp = Qt.QApplication(sys.argv)
    tb = SineWaveFlowgraph()
    tb.start()
    tb.show()

    def quitting():
        tb.stop()
        tb.wait()

    qapp.aboutToQuit.connect(quitting)
    qapp.exec_()


if __name__ == "__main__":
    main()
