#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

sys.path.append('../../ajenti/ajenti-core')
import aj
import aj.api
import aj.config
import aj.core
import aj.log
import aj.plugins
import builtins
import subprocess
from datetime import datetime

import sphinx_rtd_theme

# Fix gettext syntax
builtins._ = lambda x:x

#aj_plugin_path = aj.__path__[0][:-3]
aj_plugin_path = '../../ajenti/plugins'
lm_plugin_path = '../usr/lib/linuxmuster-webui/plugins' # Path relative to docs sources

aj.context = aj.api.Context()
aj.init()
aj.plugins.PluginManager.get(aj.context).load_all_from([
        aj.plugins.DirectoryPluginProvider(aj_plugin_path), 
        aj.plugins.DirectoryPluginProvider(lm_plugin_path)
])

extensions = ['sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.ifconfig',
    'sphinx.ext.viewcode',
    'sphinx.ext.autosummary']
autosummary_generate = True

templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'

# General information about the project.
project = 'linuxmuster-webui7'
year = datetime.now().strftime('%Y')
copyright = f'Andreas Till & Arnaud Kientz - {year}'
author = 'Andreas Till & Arnaud Kientz'

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
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
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
     'Andreas Till \\& Arnaud Kientz', 'manual'),
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

intersphinx_mapping = {'https://docs.python.org/': None}
