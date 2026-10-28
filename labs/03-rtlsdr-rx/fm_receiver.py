#!/usr/bin/env /usr/bin/python3
"""Wideband FM receiver using RTL-SDR via SoapySDR. Outputs to audio sink."""

import signal
import sys
from gnuradio import gr, analog, audio, blocks, filter as gr_filter
from gnuradio import soapy


class FMReceiver(gr.top_block):
    def __init__(self, freq=96.9e6, gain=40, ppm=0):
        gr.top_block.__init__(self, "FM Receiver")

        samp_rate = 2.4e6
        audio_rate = 48000
        fm_deviation = 75e3

        # RTL-SDR source via SoapySDR
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

        # Low-pass filter to isolate FM channel (~200 kHz)
        channel_width = 200e3
        transition = 50e3
        lpf_taps = gr_filter.firdes.low_pass(
            1.0, samp_rate, channel_width / 2, transition
        )
        self.lpf = gr_filter.fir_filter_ccf(1, lpf_taps)

        # FM demodulator
        self.demod = analog.wfm_rcv(
            quad_rate=samp_rate,
            audio_decimation=int(samp_rate / audio_rate),
        )

        # Audio output
        self.audio_sink = audio.sink(audio_rate, "", True)

        # Connect
        self.connect(self.src, self.lpf, self.demod, self.audio_sink)


def main():
    freq = float(sys.argv[1]) if len(sys.argv) > 1 else 96.9e6
    gain = float(sys.argv[2]) if len(sys.argv) > 2 else 40
    ppm = float(sys.argv[3]) if len(sys.argv) > 3 else 0

    print(f"FM Receiver: {freq / 1e6:.1f} MHz, gain={gain} dB, ppm={ppm}")
    print("Press Ctrl+C to stop")

    tb = FMReceiver(freq=freq, gain=gain, ppm=ppm)

    def handler(sig, frame):
        print("\nStopping...")
        tb.stop()
        tb.wait()
        sys.exit(0)

    signal.signal(signal.SIGINT, handler)

    tb.start()
    tb.wait()


if __name__ == "__main__":
    main()
