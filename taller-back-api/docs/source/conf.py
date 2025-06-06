# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
sys.path.insert(0, os.path.abspath('../..'))

project = 'Taller API'
copyright = '2025, Antonio Martin Sosa'
author = 'Antonio Martin Sosa'
release = '2.0.0'

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.todo",
    "sphinxcontrib.httpdomain"
]

latex_elements = {
    'preamble': r'''
\usepackage[utf8]{inputenc}
\usepackage{underscore}
\renewcommand{\sphinxbfcode}[1]{\textbf{\sphinxcode{#1}}}
\renewcommand{\sphinxupquote}[1]{\texttt{#1}}

% Cargar tabulary normalmente
\usepackage{tabulary}

% Estilo para encabezados de tablas (normal + negrita)
\renewcommand{\sphinxstyletheadfamily}{\normalfont\bfseries}
''',
}

templates_path = ['_templates']
exclude_patterns = []

language = 'es'

html_theme = 'furo'
html_static_path = ['_static']
