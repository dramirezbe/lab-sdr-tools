# Fedora Setup for SDR

Tested on Fedora 39+.

## Step 1 — System update

```bash
sudo dnf upgrade --refresh -y
```

## Step 2 — Install GNU Radio

```bash
sudo dnf install -y gnuradio
```

## Step 3 — Install SoapySDR and device drivers

```bash
# SoapySDR core
sudo dnf install -y SoapySDR SoapySDR-devel python3-soapysdr

# HackRF
sudo dnf install -y hackrf SoapyHackRF

# USRP (B200mini, B210, etc.)
sudo dnf install -y uhd uhd-firmware SoapyUHD

# RTL-SDR (optional, for receive)
sudo dnf install -y rtl-sdr SoapyRTLSDR
```

### Download UHD firmware (USRP only)

```bash
sudo uhd_images_downloader
```

> On Fedora the firmware is often included with the `uhd-firmware` package. Run the downloader only if `uhd_find_devices` reports missing images.

## Step 4 — Install Python tools

```bash
sudo dnf install -y python3-numpy python3-scipy python3-pip
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

## Step 6 — SELinux note

Fedora ships with SELinux enabled. If device access is blocked despite udev rules:

```bash
# Check for denials
sudo ausearch -m avc --ts recent

# Temporarily set permissive to test (resets on reboot)
sudo setenforce 0
```

If permissive mode fixes it, create a local policy module rather than leaving SELinux disabled.

## Step 7 — Set up the project

```bash
# Install uv if not present
curl -LsSf https://astral.sh/uv/install.sh | sh

cd lab-sdr-tools
uv venv --python /usr/bin/python3 --system-site-packages
source .venv/bin/activate
uv pip install -e .
```

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

### GNU Radio version too old

Enable RPM Fusion for newer packages:

```bash
sudo dnf install -y \
  https://mirrors.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm
sudo dnf upgrade --refresh
sudo dnf install -y gnuradio
```

### `ModuleNotFoundError: No module named 'gnuradio'`

Same as other distros — make sure the venv was created with the **system** Python and `--system-site-packages`:

```bash
uv venv --python /usr/bin/python3 --system-site-packages
```
