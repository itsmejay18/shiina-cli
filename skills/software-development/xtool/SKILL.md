---
name: xtool
description: "Use when building or signing iOS apps without Xcode."
version: 1.0.0
author: Shiina Agent (from xtool-org/xtool docs)
license: MIT
platforms: [linux, macos, windows]
metadata:
  shiina:
    tags: [ios, xcode, swiftpm, signing, appimage, usbmuxd, device-install]
    category: software-development
---

# xtool — build and sign iOS apps without Xcode

xtool replicates Xcode with open standards: build a SwiftPM package into an iOS app, sign and
install it, and drive Apple Developer Services — from Linux, Windows (WSL) or macOS.

## When to use

Reach for xtool when the target is **iOS** and Xcode is unavailable (any Linux host). For Android
release builds use `android-release-builds` instead.

## Prerequisites (Linux)

- **Swift 6.4 toolchain** — <https://swift.org/install/linux>. Not in the Arch repos; install it
  from swift.org and confirm `swift --version` reports 6.4.
- **usbmuxd** — how the host talks to the iOS device. On Arch: `sudo pacman -S usbmuxd`
  (Debian/Ubuntu: `sudo apt-get install usbmuxd`). `libimobiledevice-utils` is optional but
  useful — `ideviceinfo` reports the connected device.
- **Xcode 27 `.xip`** for the SDK, from <https://developer.apple.com/download/all/?q=Xcode>.
  That URL needs a browser session and an Apple ID, so `curl` will not fetch it.

## Install

Linux/Windows — the released AppImage:

    curl -fL "https://github.com/xtool-org/xtool/releases/latest/download/xtool-$(uname -m).AppImage" -o xtool
    chmod +x xtool
    sudo mv xtool /usr/local/bin/

macOS: `brew install xtool-org/tap/xtool`

From a source checkout: `make linux-dist` on Linux. On macOS xtool ships as an `.app` bundle
(entitlements + keychain), so build it with `make mac` and invoke `./macOS/Build/xtool`.

Verify with `xtool --help` — it prints `OVERVIEW: Cross-platform Xcode replacement`.

## Core workflow

    xtool setup          one-time setup for iOS development
    xtool auth           Apple Developer Services authentication
    xtool sdk            manage the Darwin Swift SDK
    xtool new            create a SwiftPM project
    xtool dev            build and run it
    xtool devices        list connected devices
    xtool install <ipa>  install an .ipa to a device
    xtool launch <app>   launch an installed app
    xtool ds             talk to Apple Developer Services directly

XKit is the same functionality as a SwiftPM library, for driving Apple services and devices from
an app of your own.

## Pitfalls

- Device work needs `usbmuxd` running. "No devices" is usually this, not the cable.
- Under WSL, bind the device with USBIPD first. `AFCClient.Error.muxError` is the known WSL
  symptom — relay through iTunes on Windows instead (xtool issue #19).
- Signing needs a real Apple Developer account; `xtool auth` is the gate and there is no offline
  substitute.
- Building for iOS is not the same as running it: `xtool install` needs the device present and
  trusted, so confirm with `xtool devices` before debugging a failed install.

## Source

Written for Shiina from the [xtool-org/xtool](https://github.com/xtool-org/xtool) README and
docc guides, MIT License, Copyright (c) 2024 Kabir Oberai. xtool ships no SKILL.md upstream;
this consolidates its install and CLI docs for agent use.
