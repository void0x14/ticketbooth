<div align="center">
  <h1><img src="./data/icons/hicolor/scalable/apps/io.github.void0x14.Ticketbooth.svg" height="64" alt="Ticket Booth Icon"/><br>Ticket Booth</h1>
  <h4>Keep track of your favorite shows - Professional & Maintained Edition</h4>
</div>

> [!TIP]
> **Independent Maintenance:** This is the primary, actively maintained version of Ticket Booth. 
> It features critical architectural fixes, performance optimizations (Widget Recycling), 
> and resolved dependency conflicts that are not present in original builds.

<div align="center">
  <a href="https://github.com/void0x14/ticketbooth/actions" title="Build Flatpak status">
    <img src="https://github.com/void0x14/ticketbooth/actions/workflows/build-x86.yaml/badge.svg" alt="CI workflow status"/>
  </a>
  <a href="./LICENSES/GPL-3.0-or-later.txt" title="GPL-3 License">
    <img src="https://img.shields.io/badge/License-GPL--3.0-blue.svg" alt="GPL 3 License">
  </a>
  <a href="https://hosted.weblate.org/engage/ticket-booth/">
    <img src="https://hosted.weblate.org/widget/ticket-booth/svg-badge.svg" alt="Translation status" />
  </a>
  <a href="https://stopthemingmy.app" title="Please do not theme this app">
    <img src="https://stopthemingmy.app/badge.svg" alt="Please do not theme this app"/>
  </a>
  <br />
  <a href="#features">Features</a> ·
  <a href="#screenshots">Screenshots</a> ·
  <a href="#install">Install</a> ·
  <a href="#contribute">Contribute</a> ·
  <a href="#license">License</a>
</div>

## 🗺️ The Void0x14 Roadmap: Building an Empire

This project is not just a fork; it is a **Declaration of Sovereignty**. We are rebuilding Ticket Booth to be the ultimate, unrestricted media companion. Our goal is to create a system that is performant, private, and powerful—operating entirely on your terms.

> **"We do not build apps; we build ecosystems."**

### 🌑 Phase 1: The Hardening (Current Focus)
*Reforging the core to be unbreakable and lightweight.*

- [ ] **Zero Dependency Doctrine:** Systematically removing heavy external libraries (`requests`, `Pillow`) in favor of Python Standard Library and native GNOME libs.
  - *Goal:* `<100MB` RAM usage and a bulletproof, "Black Box" codebase.
- [ ] **Surgical Logic:** Rewriting the entire network and image processing stack for maximum speed and minimal footprint.
- [ ] **UI/Logic Decoupling:** Separating the interface from the brain, paving the way for "Headless" and "Neural" modes.

### 🔗 Phase 2: The Network (Project LIFE)
*Establishing the backbone of a universal media system.*

- [ ] **Custom API Engine:** Bypassing generic wrappers to gain direct, granular control over metadata fetching.
- [ ] **Smart Routing:** Implementing intelligent networking to ensure access to data even in "restrictive" network environments.
- [ ] **Shadow Architecture:** Preparing the internal database to handle complex, decentralized data structures beyond simple lists.

### 📱 Phase 3: Expansion (The Mobile Front)
*Taking the empire to every screen.*

- [ ] **Android & iOS Port:** Bringing the verified "Void Experience" to mobile.
  - *Strategy:* A unified logic core with a native, responsive UI.
- [ ] **Dynamic Feature Delivery:** A next-gen configuration system allowing specific features and "capabilities" to be enabled remotely without app store updates.
- [ ] **Cloud-Agnostic Sync:** Sync your library across devices using your own storage, not ours.

### 🔓 Phase 4: God Mode (The Ultimate Vision)
*Total freedom and user control.*

- [ ] **The "Void" Plugin System:** A powerful, open-ended engine allowing users to extend functionality limits.
  - *Capability:* Users can load "Community Add-ons" to fetch content from *any* source they choose. We provide the engine; you choose the fuel.
- [ ] **Data Liberation:** Complete ownership of your data with advanced export/import tools.
- [ ] **System Integration:** Deep integration with the OS to make Ticket Booth feel like a native extension of your digital life.

---
*Note: This roadmap is a living document. The "Empire" is built one commit at a time.*

## Core Features

Ticket Booth allows you to build your watchlist of movies and TV Shows, keep track of watched titles, and find information about the latest releases.

*Ticket Booth does not allow you to watch or download content. This app uses the TMDB API but is not endorsed or certified by TMDB.*

## Screenshots

<div align="center">
  <img src="./data/appstream/new1.png" width="400" />
  <img src="./data/appstream/new2.png" width="400" />
  <br />
  <img src="./data/appstream/new3.png" width="400" />
  <img src="./data/appstream/new4.png" width="400" />
</div>

## Install

<a href='https://flathub.org/apps/io.github.void0x14.Ticketbooth'>
  <img width='240' alt='Download on Flathub' src='https://dl.flathub.org/assets/badges/flathub-badge-en.png'/>
</a>

Builds are available as artifacts on the [Actions page](https://github.com/void0x14/ticketbooth/actions).\
To build from source, see [Building](./CONTRIBUTING.md#building).

## Contribute

Issues and pull requests are welcome! This repository is the active development home for Ticket Booth.

This project is translated via [Weblate](https://hosted.weblate.org/engage/ticket-booth/). \
<a href="https://hosted.weblate.org/engage/ticket-booth/">
  <img src="https://hosted.weblate.org/widget/ticket-booth/horizontal-auto.svg" alt="Translation status" />
</a>

See [Contributing](./CONTRIBUTING.md) to learn more.

## License

Original Work Copyright (C) 2023-2025 Alessandro Iepure  
Maintenance & Enhancements Copyright (C) 2026 void0x14

This application comes with absolutely no warranty. See the GNU General Public
License, version 3 or later for details. A [copy of the license](./LICENSES/GPL-3.0-or-later.txt)
can be found in the [LICENSES/](./LICENSES/) folder.
