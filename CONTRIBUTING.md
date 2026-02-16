# Contributing

<!--
Copyright (C) 2023 Alessandro Iepure
Maintenance & Enhancements Copyright (C) 2026 void0x14

SPDX-License-Identifier: CC0-1.0
-->

Ticket Booth is a Linux app built with Python using the GTK4 toolkit and libadwaita. The only officially supported packaging format is Flatpak.

## Code

When contributing to the source code, use the same style and conventions present in the files already in the repo. \
All contributions are and will always be welcome.\
If you have an idea, feel free to create an issue, and let's discuss it. You can also fork the repo, make your changes, and submit a pull request to change the code yourself.

## Translations

This project is translated via [Weblate](https://hosted.weblate.org/engage/ticket-booth/) (preferred). Alternatively, you can translate manually by doing the following:

1. Clone the repository.
2. If it isn't already there, add your language to `/po/LINGUAS`.
3. Create a new translation from the `/po/ticketbooth.pot` file with a translation editor such as Poedit.
4. Save the file as `[YOUR LANGUAGE CODE].po` to `/po/`.
5. Create a pull request with your translations.

## Building

### Gnome Builder

The quickest and easiest way

1. Install GNOME Builder.
2. Click "Clone Repository" with https://github.com/void0x14/ticketbooth.git as the URL.
3. Click on the build button (hammer) at the top.

### Flatpak builder and other IDEs

```shell
git clone https://github.com/void0x14/ticketbooth
flatpak-builder --repo=/path/to/repo/dir --force-clean --user /path/to/build/dir io.github.void0x14.Ticketbooth.Devel.json
flatpak remote-add --user ticketbooth ticketbooth --no-gpg-verify
flatpak install --user ticketbooth io.github.void0x14.Ticketbooth.Devel
```

Then run with

```shell
flatpak run --user io.github.void0x14.Ticketbooth.Devel
```
