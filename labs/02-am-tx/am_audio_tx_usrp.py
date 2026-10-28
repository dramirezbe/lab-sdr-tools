#!/usr/bin/env /usr/bin/python3
"""AM transmitter: WAV file as message, carrier at 80 MHz, via USRP B200mini. Superloop."""

import signal
import sys
from gnuradio import gr, analog, blocks, filter as gr_filter, soapy


class AMAudioTxUSRP(gr.top_block):
    def __init__(self):
        gr.top_block.__init__(self, "AM Audio TX USRP")

        samp_rate = 2e6
        center_freq = 80e6
        audio_rate = 48000
        carrier_level = 0.5
        tx_gain = 50  # B200mini: 0-89.8 dB

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

        # --- USRP B200mini sink via SoapySDR ---
        self.usrp_sink = soapy.sink("driver=uhd", "fc32", 1, "", "", [""], [""])
        self.usrp_sink.set_sample_rate(0, samp_rate)
        self.usrp_sink.set_frequency(0, center_freq)
        self.usrp_sink.set_gain(0, tx_gain)

        # --- Connections ---
        self.connect((self.wav_source, 0), (self.stereo_to_mono, 0))
        self.connect((self.wav_source, 1), (self.stereo_to_mono, 1))
        self.connect(self.stereo_to_mono, self.audio_gain, self.dc_offset)
        self.connect(self.dc_offset, self.float_to_complex, (self.am_mod, 0))
        self.connect(self.carrier, (self.am_mod, 1))
        self.connect(self.am_mod, self.resampler, self.usrp_sink)


def main():
    tb = AMAudioTxUSRP()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()
        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    print("AM Audio TX on 80 MHz via USRP B200mini (looping WAV) — Ctrl+C to stop")
    tb.start()
    tb.wait()


if __name__ == "__main__":
    main()
