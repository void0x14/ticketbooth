# Copyright (C) 2023 Alessandro Iepure
#
# SPDX-License-Identifier: GPL-3.0-or-later

import gi
gi.require_version('Gdk', '4.0')
from gi.repository import Gdk, Gio, GLib
from pathlib import Path
import logging
from .app_logging.session_file_handler import SessionFileHandler
import faulthandler
import os
from concurrent.futures import ThreadPoolExecutor

APP_ID = 'me.iepure.Ticketbooth.Devel'
VERSION = '0.1-dev'
PREFIX = '/me/iepure/Ticketbooth/Devel'

# Register resources manually
try:
    resource_path = Path(__file__).parent / 'ticketbooth.gresource'
    if resource_path.exists():
        resource = Gio.Resource.load(str(resource_path))
        resource._register()
    else:
        logging.warning(f"Resource file not found at {resource_path}")
except Exception as e:
    logging.warning(f"Failed to register resources: {e}")
APP_NAME = 'Ticket Booth (Dev)'

# Ensure schema exists or mock it if needed. 
# For now, let's assume glib-compile-schemas is run or not needed if we mock?
# But checking code: schema = Gio.Settings.new(APP_ID) might fail if schema not installed.
# We might need to compile schemas.
# Let's try to run without compiling schemas first, if it fails, we compile.

schema = Gio.Settings.new(APP_ID)

data_dir = Path(GLib.get_user_data_dir())
cache_dir = Path(GLib.get_user_cache_dir())

poster_dir = data_dir / 'poster'
background_dir = data_dir / 'background'
series_dir = data_dir / 'series'

db = data_dir / 'data.db'

if not os.path.exists(data_dir/'logs'):
    os.makedirs(data_dir/'logs')
faulthandler.enable(file=open(data_dir/'logs'/'crash.log',"w"))

DEBUG = True
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filename=data_dir / 'logs' / 'ticketbooth.log')

handler = SessionFileHandler(filename=data_dir / 'logs' / 'ticketbooth.log')
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logging.getLogger().addHandler(handler)

log_files = None

# =============================================================================
# 🚀 GLOBAL OPTIMIZATION OBJECTS
# =============================================================================
# TEXTURE_CACHE: Store Gdk.Texture objects to prevent re-processing image files.
# Key: URI string, Value: Gdk.Texture
TEXTURE_CACHE = {}

# IMAGE_EXECUTOR: Dedicated thread pool for async image loading.
# Limits OS thread overhead and prevents "thread explosion".
IMAGE_EXECUTOR = ThreadPoolExecutor(max_workers=12)
