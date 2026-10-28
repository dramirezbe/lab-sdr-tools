#!/usr/bin/env /usr/bin/python3
"""AM transmitter: WAV file as message, carrier at 80 MHz, via HackRF. Superloop."""

import signal
import sys
from gnuradio import gr, analog, blocks, filter as gr_filter
from gnuradio import soapy


class AMAudioTx(gr.top_block):
    def __init__(self):
        gr.top_block.__init__(self, "AM Audio TX")

        samp_rate = 2e6
        center_freq = 80e6
        audio_rate = 48000
        carrier_level = 0.5
        if_gain = 20
        vga_gain = 20

        # --- Message: WAV file (stereo→mono, looped) ---
        self.wav_source = blocks.wavfile_source(
            "/home/javastral-gcpds/tx-AM-hackrf/message_audio.wav", True
        )
        self.stereo_to_mono = blocks.add_ff(1)

        self.audio_gain = blocks.multiply_const_ff(0.5)

        # --- AM modulation: carrier * (1 + message) ---
        self.dc_offset = blocks.add_const_ff(1.0)
        self.float_to_complex = blocks.float_to_complex(1)
        self.carrier = analog.sig_source_c(audio_rate, analog.GR_COS_WAVE, 0, carrier_level, 0)
        self.am_mod = blocks.multiply_cc(1)

        # --- Resample 48k → 2M ---
        self.resampler = gr_filter.rational_resampler_ccf(
            interpolation=int(samp_rate),
            decimation=int(audio_rate),
            taps=[],
            fractional_bw=0.4,
        )

        # --- HackRF sink via SoapySDR ---
        self.hackrf_sink = soapy.sink("driver=hackrf", "fc32", 1, "", "", [""], [""])
        self.hackrf_sink.set_sample_rate(0, samp_rate)
        self.hackrf_sink.set_frequency(0, center_freq)
        self.hackrf_sink.set_gain(0, "AMP", 0)
        self.hackrf_sink.set_gain(0, "VGA", vga_gain)

        # --- Connections ---
        self.connect((self.wav_source, 0), (self.stereo_to_mono, 0))
        self.connect((self.wav_source, 1), (self.stereo_to_mono, 1))
        self.connect(self.stereo_to_mono, self.audio_gain, self.dc_offset)
        self.connect(self.dc_offset, self.float_to_complex, (self.am_mod, 0))
        self.connect(self.carrier, (self.am_mod, 1))
        self.connect(self.am_mod, self.resampler, self.hackrf_sink)


def main():
    tb = AMAudioTx()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()
        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    print("AM Audio TX on 80 MHz (looping WAV) — Ctrl+C to stop")
    tb.start()
    tb.wait()


if __name__ == "__main__":
    main()
