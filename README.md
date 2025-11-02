# kernel-copyto

<div align="center">

[![OBS Build Status](https://img.shields.io/badge/OBS-Build_Status-brightgreen?style=flat-square)](https://build.opensuse.org/package/show/home:itachi_re/kernel-copyto)
![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Linux-lightgrey.svg)
![Shell](https://img.shields.io/badge/Shell-Bash-89e051.svg)

**A robust `kernel-install` hook for automatic kernel image synchronization**

[Features](#-features) • [Installation](#-installation) • [Configuration](#-configuration) • [Documentation](#-documentation) • [Contributing](#-contributing)

</div>

---

## 📖 Overview

`kernel-copyto` is a lightweight automation tool that bridges the gap between kernel updates and EFI bootloaders. When using modern bootloaders like `systemd-boot` or `rEFInd` that load kernels directly from the EFI System Partition (ESP), kernel updates don't automatically propagate to your boot partition. This hook ensures your bootloader always has immediate access to the latest kernel and initramfs images.

### The Problem It Solves

On traditional GRUB setups, kernel updates are handled automatically. But with direct EFI boot methods:

- ❌ New kernels install to `/boot/` but bootloader reads from ESP
- ❌ Manual copying is error-prone and easy to forget
- ❌ Bootloader may attempt to load outdated or missing kernels
- ✅ `kernel-copyto` automates this process seamlessly

---

## ✨ Features

### Core Functionality
- 🔄 **Automatic Synchronization** - Integrates with `kernel-install` lifecycle hooks
- 🎯 **Flexible Targeting** - Configurable destination paths and filename patterns
- 🔒 **Safe by Design** - Disabled by default, explicit opt-in required
- 📊 **Verbose Logging** - Clear, actionable output for every operation
- ⚡ **Zero Overhead** - Minimal resource usage, pure shell script
- 🧩 **Universal Compatibility** - Works with any bootloader requiring manual kernel placement

### Advanced Features
- 📝 Custom filename templates with version substitution
- 🛡️ Atomic operations with error handling
- 🔍 Automatic validation of source and destination paths
- 🚀 Support for both kernel installation and removal operations
- 📦 Easy integration with package managers

---

## 🛠 Installation

### Method 1: OpenSUSE (Recommended via OBS)

```bash
# Add the OBS repository
sudo zypper addrepo -f \
  https://download.opensuse.org/repositories/home:/itachi_re/openSUSE_Tumbleweed/home:itachi_re.repo

# Refresh and install
sudo zypper refresh
sudo zypper install kernel-copyto
```

### Method 2: Arch Linux (AUR)

```bash
# Using yay
yay -S kernel-copyto

# Using paru
paru -S kernel-copyto

# Manual AUR installation
git clone https://aur.archlinux.org/kernel-copyto.git
cd kernel-copyto
makepkg -si
```

### Method 3: Manual Installation (Universal)

```bash
# Clone the repository
git clone https://github.com/yourusername/kernel-copyto.git
cd kernel-copyto

# Install files
sudo install -Dm755 kernel-copyto /usr/bin/kernel-copyto
sudo install -Dm644 52-kernel-copyto.conf /etc/kernel/install.d/52-kernel-copyto.conf
sudo install -Dm644 kernel-copyto.conf /etc/kernel-copyto.conf.example

# Create your configuration
sudo cp /etc/kernel-copyto.conf.example /etc/kernel-copyto.conf
```

### Method 4: Quick Install Script

```bash
curl -fsSL https://raw.githubusercontent.com/yourusername/kernel-copyto/main/install.sh | sudo bash
```

---

## ⚙️ Configuration

### Initial Setup

1. **Create configuration file:**
   ```bash
   sudo nano /etc/kernel-copyto.conf
   ```

2. **Basic configuration:**
   ```ini
   # Enable the hook (REQUIRED - hook is disabled by default)
   enable=true
   
   # Target directory (usually on ESP)
   copydir=/boot/efi/EFI/Linux
   
   # Filename patterns (%v is replaced with kernel version)
   kernel=kernel-%v
   initrd=initrd-%v
   
   # Copy command with options
   command='cp -fvp'
   ```

### Configuration Reference

| Parameter | Description | Default | Example |
|-----------|-------------|---------|---------|
| `enable` | Enable/disable the hook | `false` | `true` |
| `copydir` | Destination directory | - | `/boot/efi/EFI/Linux` |
| `kernel` | Kernel filename pattern | `kernel-%v` | `vmlinuz-%v` |
| `initrd` | Initramfs filename pattern | `initrd-%v` | `initramfs-%v.img` |
| `command` | Copy command | `cp -fvp` | `rsync -av` |

**Pattern Variables:**
- `%v` - Full kernel version string (e.g., `6.17.6-1-default`)

### Configuration Examples

<details>
<summary><b>systemd-boot (Standard ESP Layout)</b></summary>

```ini
enable=true
copydir=/boot/efi/EFI/Linux
kernel=kernel-%v
initrd=initrd-%v
command='cp -fvp'
```
</details>

<details>
<summary><b>rEFInd (Custom Subdirectory)</b></summary>

```ini
enable=true
copydir=/boot/efi/EFI/refind/linux
kernel=vmlinuz-%v
initrd=initramfs-%v.img
command='cp -fvp'
```
</details>

<details>
<summary><b>Multi-Boot Setup</b></summary>

```ini
enable=true
copydir=/boot/efi/EFI/boot
kernel=vmlinuz-linux-%v
initrd=initramfs-linux-%v.img
command='cp -fvp --preserve=all'
```
</details>

<details>
<summary><b>Network Boot (Using rsync)</b></summary>

```ini
enable=true
copydir=/srv/tftp/boot
kernel=kernel-%v
initrd=initrd-%v
command='rsync -av --checksum'
```
</details>

---

## 🧪 Testing & Verification

### Quick Test

Manually trigger the hook with your current kernel:

```bash
sudo kernel-install add "$(uname -r)" "/boot/vmlinuz-$(uname -r)"
```

**Expected output:**
```
Copying kernel: /boot/vmlinuz-6.17.6-1-default -> /boot/efi/EFI/Linux/kernel-6.17.6-1-default
'/boot/vmlinuz-6.17.6-1-default' -> '/boot/efi/EFI/Linux/kernel-6.17.6-1-default'
Copying initrd: /boot/initrd-6.17.6-1-default -> /boot/efi/EFI/Linux/initrd-6.17.6-1-default
'/boot/initrd-6.17.6-1-default' -> '/boot/efi/EFI/Linux/initrd-6.17.6-1-default'
Kernel copy completed successfully
```

### Verification Checklist

```bash
# 1. Verify configuration is loaded
sudo kernel-copyto --check-config

# 2. List copied files
ls -lh /boot/efi/EFI/Linux/

# 3. Verify file integrity
sha256sum /boot/vmlinuz-$(uname -r)
sha256sum /boot/efi/EFI/Linux/kernel-$(uname -r)

# 4. Check hook execution in logs
journalctl -u kernel-install | tail -20
```

### Automated Testing

```bash
# Simulate kernel installation
sudo kernel-install add "$(uname -r)" "/boot/vmlinuz-$(uname -r)" --verbose

# Verify cleanup on removal
sudo kernel-install remove "$(uname -r)"
ls /boot/efi/EFI/Linux/  # Old kernel files should be removed
```

---

## 🔧 Troubleshooting

### Common Issues

<details>
<summary><b>Hook not executing</b></summary>

**Symptoms:** No output during kernel updates, files not copied

**Solutions:**
```bash
# Check if hook is enabled
grep "enable" /etc/kernel-copyto.conf

# Verify file permissions
ls -l /etc/kernel/install.d/52-kernel-copyto.conf
# Should be: -rw-r--r-- or -rwxr-xr-x

# Test hook manually
sudo /etc/kernel/install.d/52-kernel-copyto.conf add "$(uname -r)" /boot/vmlinuz-$(uname -r)
```
</details>

<details>
<summary><b>Permission denied errors</b></summary>

**Symptoms:** Copy fails with permission errors

**Solutions:**
```bash
# Check target directory permissions
ls -ld /boot/efi/EFI/Linux/
sudo chmod 755 /boot/efi/EFI/Linux/

# Verify ESP is mounted
mount | grep -i efi

# Check disk space
df -h /boot/efi
```
</details>

<details>
<summary><b>Files not found</b></summary>

**Symptoms:** "Source file not found" errors

**Solutions:**
```bash
# Locate actual kernel files
ls -la /boot/ | grep vmlinuz
ls -la /boot/ | grep initrd

# Verify kernel version format
uname -r

# Check kernel-install configuration
cat /etc/kernel/install.conf
```
</details>

<details>
<summary><b>SELinux/AppArmor conflicts</b></summary>

**Solutions:**
```bash
# SELinux: Check for denials
sudo ausearch -m avc -ts recent | grep kernel-copyto

# Create SELinux policy if needed
sudo audit2allow -a -M kernel-copyto
sudo semodule -i kernel-copyto.pp

# AppArmor: Check logs
sudo dmesg | grep -i apparmor | grep kernel-copyto
```
</details>

### Debug Mode

Enable verbose logging:

```bash
# View systemd logs
journalctl -u kernel-install -f

# Manual test with full output
sudo bash -x /usr/bin/kernel-copyto add "$(uname -r)" "/boot/vmlinuz-$(uname -r)"

# Check kernel-install environment
sudo kernel-install list
```

### Getting Help

If issues persist:

1. Check existing [GitHub Issues](https://github.com/yourusername/kernel-copyto/issues)
2. Enable debug logging and capture output
3. Include system information:
   ```bash
   uname -a
   cat /etc/os-release
   ls -la /boot/
   ls -la /boot/efi/
   cat /etc/kernel-copyto.conf
   ```

---

## 📚 Documentation

### How It Works

1. **Trigger:** Package manager updates kernel → calls `kernel-install`
2. **Hook Execution:** `kernel-install` runs scripts in `/etc/kernel/install.d/`
3. **Copy Operation:** `kernel-copyto` reads config and copies files
4. **Verification:** Logs success/failure for troubleshooting

### Architecture

```
Package Manager (zypper/apt/dnf)
    ↓
kernel-install (systemd)
    ↓
/etc/kernel/install.d/52-kernel-copyto.conf
    ↓
/usr/bin/kernel-copyto
    ↓
/etc/kernel-copyto.conf → Target Directory
```

### File Locations

| File | Purpose |
|------|---------|
| `/etc/kernel-copyto.conf` | Main configuration |
| `/etc/kernel/install.d/52-kernel-copyto.conf` | Hook script |
| `/usr/bin/kernel-copyto` | Core executable |
| `/boot/vmlinuz-*` | Source kernel images |
| `/boot/initrd-*` | Source initramfs images |

### Compatibility

| Distribution | Status | Notes |
|--------------|--------|-------|
| openSUSE Tumbleweed | ✅ Tested | Primary development platform |
| openSUSE Leap | ✅ Tested | Fully supported |
| Arch Linux | ✅ Compatible | Community maintained |
| Fedora | ✅ Compatible | Requires systemd |
| Ubuntu/Debian | ⚠️ Partial | May need hook path adjustment |
| Gentoo | ✅ Compatible | Manual installation recommended |

---

## 🤝 Contributing

Contributions are welcome! We're looking for:

- 🐛 Bug reports and fixes
- 📝 Documentation improvements
- ✨ New features and enhancements
- 🧪 Distribution-specific testing
- 🌍 Translations

### Development Workflow

```bash
# 1. Fork and clone
git clone https://github.com/yourusername/kernel-copyto.git
cd kernel-copyto

# 2. Create feature branch
git checkout -b feature/amazing-feature

# 3. Make changes and test
sudo make install
sudo kernel-install add "$(uname -r)" "/boot/vmlinuz-$(uname -r)"

# 4. Commit with conventional commits
git commit -m "feat: add support for custom pattern variables"

# 5. Push and create PR
git push origin feature/amazing-feature
```

### Coding Standards

- Follow POSIX shell scripting best practices
- Use shellcheck for linting
- Add comments for complex logic
- Update documentation for new features
- Include test cases for bug fixes

### Testing Checklist

- [ ] Tested on clean installation
- [ ] Verified with manual `kernel-install` trigger
- [ ] Checked with actual kernel update
- [ ] Tested removal operations
- [ ] Validated error handling
- [ ] Checked logs for warnings

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for full details.

```
MIT License - Copyright (c) 2024 kernel-copyto contributors
```

---

## 🙏 Acknowledgments

Special thanks to:

- **OpenSUSE Build Service** - Package hosting and distribution
- **systemd developers** - The `kernel-install` framework
- **openSUSE community** - Testing, feedback, and support
- **All contributors** - For making this project better

---

## 🔗 Related Projects

### Bootloaders
- [systemd-boot](https://www.freedesktop.org/wiki/Software/systemd/systemd-boot/) - Simple UEFI boot manager
- [rEFInd](http://www.rodsbooks.com/refind/) - Graphical UEFI boot manager
- [GRUB](https://www.gnu.org/software/grub/) - Traditional bootloader

### Tools
- [kernel-install](https://www.freedesktop.org/software/systemd/man/kernel-install.html) - systemd kernel installation framework
- [dracut](https://github.com/dracutdevs/dracut) - Initramfs infrastructure
- [mkinitcpio](https://wiki.archlinux.org/title/Mkinitcpio) - Arch Linux initramfs generator

---

## 📊 Project Status

![GitHub issues](https://img.shields.io/github/issues/itachi-re/kernel-copyto)
![GitHub pull requests](https://img.shields.io/github/issues-pr/itachi-re/kernel-copyto)
![GitHub last commit](https://img.shields.io/github/last-commit/itachi-re/kernel-copyto)
![GitHub stars](https://img.shields.io/github/stars/itachi-re/kernel-copyto?style=social)

---

<div align="center">

**[⬆ Back to Top](#kernel-copyto)**

Made with ❤️ by the open source community

</div>
