# lab-sdr-tools

SDR laboratory scripts for AM transmission using GNU Radio, HackRF One, and USRP B200mini.

## Installation tutorials

Detailed setup guides for each platform:

| Tutorial | Platform |
|----------|----------|
| [01 — WSL + USBIPD](tutorials/01-wsl-usbipd-setup.md) | Windows + WSL2 (USB passthrough) |
| [02 — Debian/Ubuntu](tutorials/02-debian-setup.md) | `apt` based |
| [03 — Arch Linux](tutorials/03-arch-setup.md) | `pacman` based |
| [04 — Fedora](tutorials/04-fedora-setup.md) | `dnf` based |
| [05 — RTL-SDR](tutorials/05-rtlsdr-setup.md) | Driver blacklist, udev, calibration |

## Quick setup (if drivers are already installed)

```bash
uv venv --python /usr/bin/python3 --system-site-packages
source .venv/bin/activate
uv pip install -e .
```

> **Note:** The `--system-site-packages` flag is required so the venv can access the system-installed GNU Radio Python bindings.

## Audio assets

Audio files (`.wav`) are excluded from the repository due to size. Place your own WAV file at:

```
assets/message_audio.wav
```

A mono 48 kHz WAV file works best for the AM audio transmitter labs.

## Labs

### Lab 01 — Basics (`labs/01-basics/`)

| File | Description |
|------|-------------|
| `sine_wave.py` | Sine wave generator with Qt time and FFT sinks |
| `sine_wave.grc` | GRC flowgraph companion |

### Lab 02 — AM Transmission (`labs/02-am-tx/`)

| File | Description |
|------|-------------|
| `am_noise_tx.py` | AM transmitter with noise as modulating signal (HackRF) |
| `am_audio_tx_hackrf.py` | AM transmitter with WAV audio via HackRF |
| `am_audio_tx_usrp.py` | AM transmitter with WAV audio via USRP B200mini |
| `am_noise_tx.grc` | GRC flowgraph for noise AM TX |
| `am_audio_tx.grc` | GRC flowgraph for audio AM TX |

### Lab 03 — RTL-SDR Receive (`labs/03-rtlsdr-rx/`)

| File | Description |
|------|-------------|
| `fm_receiver.py` | Wideband FM receiver with audio output |
| `spectrum_waterfall.py` | Real-time spectrum analyzer + waterfall display (Qt GUI) |
| `fm_receiver.grc` | GRC flowgraph for FM receiver |
| `spectrum_waterfall.grc` | GRC flowgraph for spectrum/waterfall |

## Usage

```bash
source .venv/bin/activate

# Run a lab script directly
python labs/02-am-tx/am_audio_tx_hackrf.py

# Or open in GNU Radio Companion
gnuradio-companion labs/02-am-tx/am_audio_tx.grc
```

## Hardware tested

- **HackRF One** — via SoapySDR (`driver=hackrf`) — TX/RX
- **USRP B200mini** — via SoapySDR (`driver=uhd`) — TX/RX
- **RTL-SDR** (RTL2832U + R820T2) — via SoapySDR (`driver=rtlsdr`) — RX only
