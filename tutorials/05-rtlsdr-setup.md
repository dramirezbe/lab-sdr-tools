# RTL-SDR Setup Guide

RTL-SDR dongles (based on the RTL2832U chip) are inexpensive USB receivers covering approximately 24 MHz to 1.7 GHz. They are receive-only devices.

## Supported dongles

| Chip | Tuner | Typical frequency range |
|------|-------|------------------------|
| RTL2832U | R820T/R820T2 | 24 MHz – 1.766 GHz |
| RTL2832U | E4000 | 52 MHz – 2.2 GHz (with gap ~1100–1250 MHz) |
| RTL2832U | FC0012 | 22 MHz – 948 MHz |

The R820T2 variant is the most common and recommended.

## Installation by distro

### Arch Linux (pacman)

```bash
sudo pacman -S rtl-sdr soapyrtlsdr
```

### Debian / Ubuntu (apt)

```bash
sudo apt install -y rtl-sdr soapysdr-module-rtlsdr
```

### Fedora (dnf)

```bash
sudo dnf install -y rtl-sdr SoapyRTLSDR
```

### WSL2

Follow [01-wsl-usbipd-setup.md](01-wsl-usbipd-setup.md) first to pass the USB device, then install the packages above for your WSL distro.

## Blacklist the default DVB-T driver

Linux loads `dvb_usb_rtl28xxu` by default, which blocks SDR use. Blacklist it:

```bash
sudo tee /etc/modprobe.d/blacklist-rtlsdr.rules << 'EOF'
blacklist dvb_usb_rtl28xxu
blacklist rtl2832
blacklist rtl2830
EOF

sudo modprobe -r dvb_usb_rtl28xxu 2>/dev/null
```

Unplug and replug the dongle after blacklisting.

## Udev rules (non-root access)

```bash
sudo tee /etc/udev/rules.d/99-rtlsdr.rules << 'EOF'
# RTL-SDR (RTL2832U)
SUBSYSTEM=="usb", ATTR{idVendor}=="0bda", ATTR{idProduct}=="2838", MODE="0666"
SUBSYSTEM=="usb", ATTR{idVendor}=="0bda", ATTR{idProduct}=="2832", MODE="0666"
EOF

sudo udevadm control --reload-rules
sudo udevadm trigger
```

## Verify

```bash
# Basic test (should show device info and sample rates)
rtl_test

# SoapySDR detection
SoapySDRUtil --find="driver=rtlsdr"

# Quick FM listen test (tune to a local FM station, e.g. 96.9 MHz)
rtl_fm -f 96.9e6 -M wbfm -s 200000 -r 48000 - | aplay -r 48000 -f S16_LE
```

## Common parameters

| Parameter | Typical value | Notes |
|-----------|--------------|-------|
| Sample rate | 1.024 – 2.4 Msps | 2.4 Msps max stable |
| Frequency range | 24 MHz – 1.766 GHz | R820T2 tuner |
| RF gain | 0 – 49.6 dB | Use `rtl_test -t` to list gain values |
| PPM correction | varies per dongle | Calibrate with a known signal |
| Bandwidth | ≈ sample rate | No independent BW control |

## Troubleshooting

### `No supported devices found`

- Check `lsusb` for `0bda:2838` or similar
- Make sure DVB-T driver is blacklisted (see above)
- Try a different USB port

### Dropped samples

- Lower sample rate (try 1.024 Msps)
- Use USB 2.0 port directly, not through a hub
- Close other USB-intensive devices

### PPM offset (frequency drift)

Every dongle has a crystal offset. Calibrate:

```bash
# Use a known signal (e.g. GSM base station)
rtl_test -p
# Note the PPM value and pass it to your scripts
```
