#!/usr/bin/env /usr/bin/python3
"""AM transmitter: noise as message, carrier at 80 MHz, via HackRF. Runs in a superloop."""

import signal
import sys
from gnuradio import gr, analog, blocks, filter as gr_filter
import osmosdr


class AMNoiseTx(gr.top_block):
    def __init__(self):
        gr.top_block.__init__(self, "AM Noise TX")

        samp_rate = 2e6
        center_freq = 80e6
        audio_rate = 48000
        am_carrier_level = 0.5
        modulation_index = 0.5
        rf_gain = 0  # HackRF: 0 or 14 dB
        if_gain = 20  # HackRF: 0-47 dB
        bb_gain = 20  # HackRF: 0-62 dB (TX mode)

        # --- Message: band-limited noise (300-5000 Hz) ---
        self.noise = analog.noise_source_f(analog.GR_GAUSSIAN, modulation_index, 0)
        self.lpf = gr_filter.fir_filter_fff(
            1,
            gr_filter.firdes.low_pass(1, audio_rate, 5000, 1000, gr_filter.firdes.WIN_HAMMING),
        )

        # --- AM modulation: output = carrier * (1 + message) ---
        self.dc_offset = blocks.add_const_ff(1.0)
        self.carrier = analog.sig_source_c(audio_rate, analog.GR_COS_WAVE, 0, am_carrier_level, 0)
        self.float_to_complex = blocks.float_to_complex(1)
        self.am_mod = blocks.multiply_cc(1)

        # --- Resample to SDR rate ---
        self.resampler = gr_filter.rational_resampler_ccf(
            interpolation=int(samp_rate),
            decimation=int(audio_rate),
            taps=[],
            fractional_bw=0.4,
        )

        # --- HackRF sink ---
        self.hackrf_sink = osmosdr.sink(args="numchan=1 hackrf=0")
        self.hackrf_sink.set_sample_rate(samp_rate)
        self.hackrf_sink.set_center_freq(center_freq, 0)
        self.hackrf_sink.set_freq_corr(0, 0)
        self.hackrf_sink.set_gain(rf_gain, 0)
        self.hackrf_sink.set_if_gain(if_gain, 0)
        self.hackrf_sink.set_bb_gain(bb_gain, 0)
        self.hackrf_sink.set_antenna("", 0)
        self.hackrf_sink.set_bandwidth(0, 0)

        # --- Connections ---
        # noise → LPF → +1 DC → float_to_complex → multiply(carrier) → resample → HackRF
        self.connect(self.noise, self.lpf, self.dc_offset)
        self.connect(self.dc_offset, self.float_to_complex, (self.am_mod, 0))
        self.connect(self.carrier, (self.am_mod, 1))
        self.connect(self.am_mod, self.resampler, self.hackrf_sink)


def main():
    tb = AMNoiseTx()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()
        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    print("AM Noise TX on 80 MHz — Ctrl+C to stop")
    tb.start()
    tb.wait()  # superloop: blocks here until stopped


if __name__ == "__main__":
    main()
