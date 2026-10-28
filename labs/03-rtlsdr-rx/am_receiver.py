#!/usr/bin/env /usr/bin/python3
"""AM receiver using RTL-SDR via SoapySDR. Envelope detector with audio output."""

import signal
import sys
from gnuradio import gr, analog, audio, blocks, filter as gr_filter
from gnuradio import soapy


class AMReceiver(gr.top_block):
    def __init__(self, freq=80e6, gain=40, ppm=0):
        gr.top_block.__init__(self, "AM Receiver")

        samp_rate = 2.4e6
        audio_rate = 48000
        channel_width = 10e3

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

        # Decimation to narrow channel
        channel_rate = 48000
        decimation = int(samp_rate / channel_rate)

        # Band-pass around the AM signal
        lpf_taps = gr_filter.firdes.low_pass(
            1.0, samp_rate, channel_width, channel_width * 0.5
        )
        self.lpf = gr_filter.fir_filter_ccf(decimation, lpf_taps)

        # AM demod (envelope detector: complex → magnitude)
        self.am_demod = blocks.complex_to_mag(1)

        # DC blocker to remove carrier offset
        self.dc_blocker = gr_filter.dc_blocker_ff(32, True)

        # AGC to normalize audio level
        self.agc = analog.agc_ff(1e-3, 0.5, 1.0)

        # Audio output
        self.audio_sink = audio.sink(audio_rate, "", True)

        # Connect
        self.connect(self.src, self.lpf, self.am_demod, self.dc_blocker, self.agc, self.audio_sink)


def main():
    freq = float(sys.argv[1]) if len(sys.argv) > 1 else 80e6
    gain = float(sys.argv[2]) if len(sys.argv) > 2 else 40
    ppm = float(sys.argv[3]) if len(sys.argv) > 3 else 0

    print(f"AM Receiver: {freq / 1e6:.1f} MHz, gain={gain} dB, ppm={ppm}")
    print("Press Ctrl+C to stop")

    tb = AMReceiver(freq=freq, gain=gain, ppm=ppm)

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
