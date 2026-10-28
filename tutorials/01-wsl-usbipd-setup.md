# WSL + USBIPD Setup for SDR

This guide covers how to pass USB SDR devices (HackRF, USRP, RTL-SDR) from Windows into a WSL2 Linux distribution using **usbipd-win**.

> **Important:** All work happens inside WSL. Do not install GNU Radio or SDR tools on Windows.

## Prerequisites

- Windows 10 (21H2+) or Windows 11
- WSL2 with a Linux distribution installed (Ubuntu 22.04+ recommended)
- Administrator access on Windows

## Step 1 — Install usbipd-win (Windows side)

Open **PowerShell as Administrator**:

```powershell
winget install usbipd
```

After installation, restart your terminal.

## Step 2 — Install USB/IP client (WSL side)

Inside your WSL distribution:

```bash
sudo apt update
sudo apt install linux-tools-generic hwdata
sudo update-alternatives --install /usr/local/bin/usbip usbip /usr/lib/linux-tools/*-generic/usbip 20
```

## Step 3 — Identify and attach your SDR device

Plug in the SDR device. In **PowerShell as Administrator**:

```powershell
# List USB devices
usbipd list
```

Look for your device:

| Device | Typical USB ID |
|--------|---------------|
| HackRF One | `1d50:6089` |
| USRP B200mini | `2500:0020` |
| RTL-SDR | `0bda:2838` |

Bind and attach it to WSL:

```powershell
# Bind the device (first time only)
usbipd bind --busid <BUSID>

# Attach to WSL
usbipd attach --wsl --busid <BUSID>
```

Replace `<BUSID>` with the bus ID shown by `usbipd list` (e.g., `1-3`).

## Step 4 — Verify inside WSL

```bash
# Check device is visible
lsusb

# For HackRF
hackrf_info

# For USRP
uhd_find_devices

# For RTL-SDR
rtl_test
```

## Step 5 — Install SDR tools inside WSL

Follow the tutorial for your WSL distro:

- Ubuntu/Debian → [02-debian-setup.md](02-debian-setup.md)
- Arch (if using ArchWSL) → [03-arch-setup.md](03-arch-setup.md)
- Fedora (if using Fedora Remix for WSL) → [04-fedora-setup.md](04-fedora-setup.md)

## Reconnecting after reboot

USB devices detach when WSL restarts. Re-attach from PowerShell:

```powershell
usbipd attach --wsl --busid <BUSID>
```

## Troubleshooting

### Device not showing in `lsusb`

- Make sure WSL2 is used, not WSL1: `wsl --set-version <distro> 2`
- Re-run `usbipd attach --wsl --busid <BUSID>` as Administrator

### Permission denied on device

Add udev rules inside WSL:

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

### Display/GUI for GNU Radio Companion

Install an X server on Windows (e.g., VcXsrv, X410) or use WSLg (Windows 11):

```bash
# Test GUI
gnuradio-companion
```
