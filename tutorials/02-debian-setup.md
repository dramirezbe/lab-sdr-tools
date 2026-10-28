# Debian/Ubuntu Setup for SDR

Tested on Ubuntu 22.04+ and Debian 12+.

## Step 1 — System update

```bash
sudo apt update && sudo apt upgrade -y
```

## Step 2 — Install GNU Radio

```bash
sudo apt install -y gnuradio
```

This pulls in Python bindings, Qt GUI components, and core DSP blocks.

## Step 3 — Install SoapySDR and device drivers

```bash
# SoapySDR core
sudo apt install -y soapysdr-tools python3-soapysdr

# HackRF
sudo apt install -y hackrf soapysdr-module-hackrf

# USRP (B200mini, B210, etc.)
sudo apt install -y uhd-host soapysdr-module-uhd

# RTL-SDR (optional, for receive)
sudo apt install -y rtl-sdr soapysdr-module-rtlsdr
```

### Download UHD firmware (USRP only)

```bash
sudo uhd_images_downloader
```

## Step 4 — Install Python tools

```bash
sudo apt install -y python3-pip python3-venv python3-numpy python3-scipy
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

## Step 6 — Set up the project

```bash
# Install uv if not present
curl -LsSf https://astral.sh/uv/install.sh | sh

cd lab-sdr-tools
uv venv --python python3 --system-site-packages
source .venv/bin/activate
uv pip install -e .
```

## Step 7 — Verify

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

### `gnuradio` package version too old

Ubuntu repos may ship GNU Radio 3.8 or 3.9. For 3.10+:

```bash
sudo add-apt-repository ppa:gnuradio/gnuradio-releases
sudo apt update
sudo apt install gnuradio
```

### `ModuleNotFoundError: No module named 'gnuradio'`

Make sure you created the venv with `--system-site-packages` and used the system Python, not a version manager (pyenv, mise, asdf):

```bash
uv venv --python /usr/bin/python3 --system-site-packages
```
