# Copyright (C) 2023 Alessandro Iepure
# Maintenance & Enhancements Copyright (C) 2026 void0x14
#
# SPDX-License-Identifier: GPL-3.0-or-later

pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
modelsdir = join_paths(pkgdatadir, 'src/models')

sources = [
  '__init__.py',
  'search_result_model.py',
  'language_model.py',
  'movie_model.py',
  'episode_model.py',
  'season_model.py',
  'series_model.py',
]

install_data(sources, install_dir: modelsdir)
