# Copyright (C) 2023 Alessandro Iepure
# Maintenance & Enhancements Copyright (C) 2026 void0x14
#
# SPDX-License-Identifier: GPL-3.0-or-later

desktop_file = i18n.merge_file(
        input: configure_file(
          input: 'io.github.void0x14.Ticketbooth.desktop.in',
          output: app_id + '.desktop.in',
          configuration: conf
        ),
       output: app_id + '.desktop',
         type: 'desktop',
       po_dir: '../po',
      install: true,
  install_dir: join_paths(get_option('datadir'), 'applications')
)

desktop_utils = find_program('desktop-file-validate', required: false)
if desktop_utils.found()
  test('Validate desktop file', desktop_utils, args: [desktop_file])
endif

appstream_file = i18n.merge_file(
        input: configure_file(
          input: 'io.github.void0x14.Ticketbooth.metainfo.xml.in',
          output: app_id + '.metainfo.xml.in',
          configuration: conf
        ),
       output: app_id + '.metainfo.xml',
       po_dir: '../po',
      install: true,
  install_dir: join_paths(get_option('datadir'), 'metainfo')
)

appstreamcli = find_program('appstreamcli', required: false)
if appstreamcli.found()
  test('Validate appstream file', appstreamcli, args: ['validate', appstream_file])
endif

install_data(
  configure_file(
    input: 'io.github.void0x14.Ticketbooth.gschema.xml.in',
    output: app_id + '.gschema.xml',
    configuration: conf
  ),
  install_dir: join_paths(get_option('datadir'), 'glib-2.0/schemas')
)


compile_schemas = find_program('glib-compile-schemas', required: false)
if compile_schemas.found()
  test('Validate schema file',
       compile_schemas,
       args: ['--strict', '--dry-run', meson.current_source_dir()])
endif

subdir('icons')
