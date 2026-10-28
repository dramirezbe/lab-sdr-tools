# Arch Linux Setup for SDR

Tested on Arch Linux (omarchy kernel 7.2.5) with pacman.

## Step 1 — System update

```bash
sudo pacman -Syu
```

## Step 2 — Install GNU Radio

```bash
sudo pacman -S gnuradio
```

This installs GNU Radio 3.10+ with Python bindings, Qt GUI, and core blocks.

## Step 3 — Install SoapySDR and device drivers

```bash
# SoapySDR core
sudo pacman -S soapysdr

# HackRF
sudo pacman -S hackrf soapyhackrf

# USRP (B200mini, B210, etc.)
sudo pacman -S libuhd soapyuhd

# RTL-SDR (optional, for receive)
sudo pacman -S rtl-sdr soapyrtlsdr
```

### Download UHD firmware (USRP only)

```bash
sudo uhd_images_downloader
```

## Step 4 — Install Python tools

```bash
sudo pacman -S python-numpy python-scipy python-pip
```

## Step 5 — Udev rules (non-root device access)

```bash
sudo tee /etc/udev/rules.d/99-sdr.rules << 'EOF'
# HackRF
ATTR{idVendor}=="1d50", ATTR{idProduct}=="6089", MODE="0666"
# USRP
ATTR{idVendor}=="2500", ATTR{idProduct}=="0020", MODE="0666"
# RTL-SDR
ATTR{idVendor}=="0bda", ATTR{idProduct}=="2838", MODE="0666"
EOF

sudo udevadm control --reload-rules
sudo udevadm trigger
```

Unplug and replug your device after applying rules.

## Step 6 — Disable ASPM for MT7902 WiFi (ASUS Vivobook)

If you have the MediaTek MT7902 WiFi chip and experience latency issues while using USB SDR devices:

```bash
sudo tee /etc/modprobe.d/mt7921e.conf << 'EOF'
options mt7921e disable_aspm=Y
EOF
```

This prevents USB bandwidth competition from ASPM power state transitions.

## Step 7 — Set up the project

```bash
# Install uv if not present
curl -LsSf https://astral.sh/uv/install.sh | sh

cd lab-sdr-tools
uv venv --python /usr/bin/python3 --system-site-packages
source .venv/bin/activate
uv pip install -e .
```

> **Important:** Use `/usr/bin/python3` explicitly. If you use a version manager (mise, pyenv, asdf), its Python will not see system-installed gnuradio.

## Step 8 — Verify

```bash
# GNU Radio
python3 -c "from gnuradio import gr; print('GNU Radio', gr.version())"

# SoapySDR
SoapySDRUtil --info

# HackRF
hackrf_info

# USRP
uhd_find_devices

# Run a lab
python3 labs/01-basics/sine_wave.py
```

## Troubleshooting

### `SoapySDRUtil --find` returns empty

Check the driver module is loaded:

```bash
SoapySDRUtil --info | grep -i hackrf
```

If missing, reinstall the Soapy module for your device.

### HackRF USB errors

Try a different USB port (USB 2.0 preferred for HackRF). If behind a hub, connect directly.

### `ModuleNotFoundError: No module named 'gnuradio'`

Verify which Python you are using:

```bash
which python3
python3 -c "import sys; print(sys.path)"
```

The system site-packages (`/usr/lib/python3.*/site-packages`) must be in the path.
