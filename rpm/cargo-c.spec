Name:           cargo-c
Version:        0.9.31
Release:        1
Summary:        Helper to build and install c-like libraries from Rust
License:        MIT
Group:          Development/Languages/Rust

URL:            https://crates.io/crates/cargo-c
Source0:        %{name}-%{version}.tar.xz
BuildRequires:  cargo >= 0.80.0
BuildRequires:  rust-std-static§
BuildRequires:  pkgconfig(openssl)
BuildRequires:  cargo-packaging

Patch1:         0001-Pin-versions-and-features-for-Rust-1.75.patch

%description
The is a cargo applet to build and install C-ABI compatibile dynamic and static
libraries from Rust.

It produces and installs a correct pkg-config file, a static library and a
dynamic library, and a C header to be used by any C (and C-compatible)
software.

%prep
%autosetup -p1 -n cargo-c

# We have to provide our own Cargo.lock for Rust 1.75
cp rpm/Cargo.lock %{name}/

%build

# https://git.sailfishos.org/mer-core/gecko-dev/blob/master/rpm/xulrunner-qt5.spec#L224
# When cross-compiling under SB2 rust needs to know what arch to emit
# when nothing is specified on the command line. That usually defaults
# to "whatever rust was built as" but in SB2 rust is accelerated and
# would produce x86 so this is how it knows differently. Not needed
# for native x86 builds
%ifarch %arm
export SB2_RUST_TARGET_TRIPLE=armv7-unknown-linux-gnueabihf
export CFLAGS_armv7_unknown_linux_gnueabihf=$CFLAGS
export CXXFLAGS_armv7_unknown_linux_gnueabihf=$CXXFLAGS
%endif
%ifarch aarch64
export SB2_RUST_TARGET_TRIPLE=aarch64-unknown-linux-gnu
export CFLAGS_aarch64_unknown_linux_gnu=$CFLAGS
export CXXFLAGS_aarch64_unknown_linux_gnu=$CXXFLAGS
%endif
%ifarch %ix86
export SB2_RUST_TARGET_TRIPLE=i686-unknown-linux-gnu
export CFLAGS_i686_unknown_linux_gnu=$CFLAGS
export CXXFLAGS_i686_unknown_linux_gnu=$CXXFLAGS
%endif

export CFLAGS="-O2 -g -pipe -Wall -Wp,-D_FORTIFY_SOURCE=2 -fexceptions -fstack-protector --param=ssp-buffer-size=4 -Wformat -Wformat-security -fmessage-length=0"
export CXXFLAGS=$CFLAGS
# This avoids a malloc hang in sb2 gated calls to execvp/dup2/chdir
# during fork/exec. It has no effect outside sb2 so doesn't hurt
# native builds.
# export SB2_RUST_EXECVP_SHIM="/usr/bin/env LD_PRELOAD=/usr/lib/libsb2/libsb2.so.1 /usr/bin/env"
# export SB2_RUST_USE_REAL_EXECVP=Yes
# export SB2_RUST_USE_REAL_FN=Yes
# export SB2_RUST_NO_SPAWNVP=Yes

%ifnarch %ix86
export HOST_CC=host-cc
export HOST_CXX=host-cxx
export CC_i686_unknown_linux_gnu=$HOST_CC
export CXX_i686_unknown_linux_gnu=$HOST_CXX
%endif

# Set meego cross compilers
export PATH=/opt/cross/bin/:$PATH
export CARGO_TARGET_ARMV7_UNKNOWN_LINUX_GNUEABIHF_LINKER=armv7hl-meego-linux-gnueabi-gcc
export CC_armv7_unknown_linux_gnueabihf=armv7hl-meego-linux-gnueabi-gcc
export CXX_armv7_unknown_linux_gnueabihf=armv7hl-meego-linux-gnueabi-g++
export AR_armv7_unknown_linux_gnueabihf=armv7hl-meego-linux-gnueabi-ar
export CARGO_TARGET_AARCH64_UNKNOWN_LINUX_GNU_LINKER=aarch64-meego-linux-gnu-gcc
export CC_aarch64_unknown_linux_gnu=aarch64-meego-linux-gnu-gcc
export CXX_aarch64_unknown_linux_gnu=aarch64-meego-linux-gnu-g++
export AR_aarch64_unknown_linux_gnu=aarch64-meego-linux-gnu-ar

export PKG_CONFIG_ALLOW_CROSS_i686_unknown_linux_gnu=1
export PKG_CONFIG_ALLOW_CROSS_armv7_unknown_linux_gnueabihf=1
export PKG_CONFIG_ALLOW_CROSS_aarch64_unknown_linux_gnu=1

cargo auditable build -j1 --offline --release --verbose --manifest-path %{name}/Cargo.toml

%install

%ifarch %arm
export SB2_RUST_TARGET_TRIPLE=armv7-unknown-linux-gnueabihf
%endif
%ifarch aarch64
export SB2_RUST_TARGET_TRIPLE=aarch64-unknown-linux-gnu
%endif
%ifarch %ix86
export SB2_RUST_TARGET_TRIPLE=i686-unknown-linux-gnu
%endif

install -D %{name}/target/$SB2_RUST_TARGET_TRIPLE/release/cargo-capi %{buildroot}%{_bindir}/cargo-capi
install %{name}/target/$SB2_RUST_TARGET_TRIPLE/release/cargo-cbuild %{buildroot}%{_bindir}/cargo-cbuild
install %{name}/target/$SB2_RUST_TARGET_TRIPLE/release/cargo-cinstall %{buildroot}%{_bindir}/cargo-cinstall
install %{name}/target/$SB2_RUST_TARGET_TRIPLE/release/cargo-ctest %{buildroot}%{_bindir}/cargo-ctest

find %{buildroot} -name .crates2.json -delete
rm -rf %{buildroot}%{_datadir}/cargo/registry

%files
%{_bindir}/cargo-capi
%{_bindir}/cargo-cbuild
%{_bindir}/cargo-cinstall
%{_bindir}/cargo-ctest
