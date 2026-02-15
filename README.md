<div align="center">
  <h1><img src="./data/icons/hicolor/scalable/apps/me.iepure.Ticketbooth.svg" height="64" alt="Ticket Booth Icon"/><br>Ticket Booth</h1>
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
  <a href="https://stopthemingmy.app" title="Please do not theme this app">
    <img src="https://stopthemingmy.app/badge.svg" alt="Please do not theme this app"/>
  </a>
  <br />
  <a href="#features">Features</a> ·
  <a href="#install">Install</a> ·
  <a href="#contribute">Contribute</a> ·
  <a href="#license">License</a>
</div>

## Key Improvements (by void0x14)

Unlike the original codebase, this version provides:

* **Modernized Architecture:** Fully refactored and standardized in English for global development.
* **Memory Efficiency:** Integrated **Widget Recycling** in `ContentGridView` to ensure fluid performance.
* **Stable Logging:** Fixed the critical namespace collisions that affected Python's standard library.
* **Security First:** Audited SQL queries with full parameterization.

## Core Features

Ticket Booth allows you to build your watchlist of movies and TV Shows, keep track of watched titles, and find information about the latest releases.

*Ticket Booth does not allow you to watch or download content. This app uses the TMDB API but is not endorsed or certified by TMDB.*

## Install

Builds are available as artifacts on the [Actions page](https://github.com/void0x14/ticketbooth/actions).\
To build from source, see [Building](./CONTRIBUTING.md#building).

## Contribute

Issues and pull requests are welcome! This repository is the active development home for Ticket Booth.

See [Contributing](./CONTRIBUTING.md) to learn more.

## License

Original Work Copyright (C) 2023-2025 Alessandro Iepure  
Maintenance & Enhancements Copyright (C) 2026 void0x14

This application comes with absolutely no warranty. See the GNU General Public
License, version 3 or later for details. A [copy of the license](./LICENSES/GPL-3.0-or-later.txt)
can be found in the [LICENSES/](./LICENSES/) folder.
