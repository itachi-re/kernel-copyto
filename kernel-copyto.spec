Name: kernel-copyto
Version: 2
Release: 1
Summary: Kernel copyto configurations for kernel-install
License: GPL-3.0-or-later
URL: https://github.com/yourusername/kernel-copyto
BuildArch: noarch

%description
%{summary}.

%prep
# Nothing to prepare for a noarch package

%build
# Nothing to build for a noarch package

%install
mkdir -p %{buildroot}%{_sysconfdir}/kernel/install.d
mkdir -p %{buildroot}%{_bindir}

# Create the kernel-install hook
cat > %{buildroot}%{_sysconfdir}/kernel/install.d/52-%{name}.conf << 'EOF'
#!/bin/sh
# This hook copies kernel and initrd to another location (e.g., EFI partition)

if [ -f %{_sysconfdir}/kernel-copyto.conf ]; then
    . %{_sysconfdir}/kernel-copyto.conf
else
    # Default to disabled if config doesn't exist
    enable=false
fi

if [ "$1" = "add" ] && [ "$enable" = "true" ]; then
    kernel_version="$2"
    kernel_image="$3"
    initrd_image="$4"
    
    %{_bindir}/%{name} --version "$kernel_version" --kernel "$kernel_image" --initrd "$initrd_image"
fi
EOF

chmod 0755 %{buildroot}%{_sysconfdir}/kernel/install.d/52-%{name}.conf

# Create main configuration file
cat > %{buildroot}%{_sysconfdir}/%{name}.conf << 'EOF'
# Enable/disable kernel copying
enable=false

# Destination directory (typically EFI partition)
copydir=/boot/efi/EFI/Linux

# Kernel image filename pattern
kernel=kernel-%v

# Initrd filename pattern  
initrd=initrd-%v

# Copy command (preserve timestamps, verbose)
command='cp -fvp'
EOF

# Create the main executable script
cat > %{buildroot}%{_bindir}/%{name} << 'EOF'
#!/bin/bash

# Default values
version=""
kernel=""
initrd=""
copydir="/boot/efi/EFI/Linux"
command="cp -fvp"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --version)
            version="$2"
            shift 2
            ;;
        --kernel)
            kernel="$2"
            shift 2
            ;;
        --initrd)
            initrd="$2"
            shift 2
            ;;
        --copydir)
            copydir="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Load configuration if exists
if [ -f /etc/kernel-copyto.conf ]; then
    . /etc/kernel-copyto.conf
fi

# Validate required parameters
if [ -z "$version" ] || [ -z "$kernel" ] || [ -z "$initrd" ]; then
    echo "Error: Missing required parameters" >&2
    exit 1
fi

# Create destination directory if it doesn't exist
mkdir -p "$copydir" || {
    echo "Error: Cannot create directory $copydir" >&2
    exit 1
}

# Function to replace %v with version in filename
format_filename() {
    local filename="$1"
    echo "${filename//%v/$version}"
}

# Copy kernel image
kernel_dest="$copydir/$(format_filename "${kernel}")"
if [ -f "$kernel" ]; then
    echo "Copying kernel: $kernel -> $kernel_dest"
    eval $command "\"$kernel\"" "\"$kernel_dest\""
else
    echo "Warning: Kernel image not found: $kernel" >&2
fi

# Copy initrd
initrd_dest="$copydir/$(format_filename "${initrd}")"
if [ -f "$initrd" ]; then
    echo "Copying initrd: $initrd -> $initrd_dest"
    eval $command "\"$initrd\"" "\"$initrd_dest\""
else
    echo "Warning: Initrd image not found: $initrd" >&2
fi

echo "Kernel copy completed successfully"
EOF

chmod 0755 %{buildroot}%{_bindir}/%{name}

%files
%defattr(-,root,root,-)
%{_bindir}/%{name}
%config(noreplace) %{_sysconfdir}/%{name}.conf
%config %{_sysconfdir}/kernel/install.d/52-%{name}.conf
%dir %{_sysconfdir}/kernel/
%dir %{_sysconfdir}/kernel/install.d/

%changelog
* Sun Nov 02 2025 itachi_re <itachi_re@protonmail.com> - 2-1
- Fixed shell script syntax issues
- Improved error handling and validation
- Simplified configuration and hook logic
- Added proper file permissions
- Fixed variable substitution in filenames
