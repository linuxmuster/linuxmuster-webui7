#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
from datetime import datetime

import sphinx_rtd_theme

extensions = ['sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.ifconfig',
    'sphinx.ext.viewcode',
    'sphinx.ext.autosummary',
    'autoapi.extension']
autosummary_generate = True

# The API reference is generated statically from the plugins' source by
# sphinx-autoapi (no import of aj/the plugins needed, unlike automodule),
# the same way as linuxmuster-tools. This keeps it in sync automatically
# as plugins are added or renamed.
autoapi_dirs = ['../usr/lib/linuxmuster-webui/plugins']
autoapi_type = 'python'
autoapi_ignore = ['*/conf.py', '*/resources/*', '*/locale/*', '*/migrations/*', '*/pytests/*', '*/test_*']
autoapi_options = ['members', 'undoc-members', 'show-inheritance', 'special-members']

templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'

# General information about the project.
project = 'linuxmuster-webui7'
year = datetime.now().strftime('%Y')
copyright = f'Arnaud Kientz - {year}'
author = 'Arnaud Kientz'

def setup(app):
    app.add_css_file("theme_overrides.css")

version = subprocess.check_output('apt-cache policy linuxmuster-webui7 | grep Candidat', shell=True).decode().split(':')[1].strip()
release = version

language = 'en_GB'
exclude_patterns = []
pygments_style = 'sphinx'
todo_include_todos = False

html_theme = 'sphinx_rtd_theme'
html_logo = '_static/logo.png'
html_static_path = ['_static']
html_sidebars = {
    '**': [
        'relations.html',  # needs 'show_related': True theme option to display
        'searchbox.html',
    ]
}

htmlhelp_basename = 'linuxmuster-webui7doc'

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #
    # 'papersize': 'letterpaper',

    # The font size ('10pt', '11pt' or '12pt').
    #
    # 'pointsize': '10pt',

    # Additional stuff for the LaTeX preamble.
    #
    # 'preamble': '',

    # Latex figure (float) alignment
    #
    # 'figure_align': 'htbp',
}

latex_documents = [
    (master_doc, 'linuxmuster-webui7.tex', 'linuxmuster-webui7 Documentation',
     author, 'manual'),
]

man_pages = [
    (master_doc, 'linuxmuster-webui7', 'linuxmuster-webui7 Documentation',
     [author], 1)
]


texinfo_documents = [
    (master_doc, 'linuxmuster-webui7', 'linuxmuster-webui7 Documentation',
     author, 'linuxmuster-webui7', 'One line description of project.',
     'Miscellaneous'),
]

intersphinx_mapping = {'python': ('https://docs.python.org/3', None)}
