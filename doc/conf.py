# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

from datetime import datetime

import intake_sdmx

# -- Project information -----------------------------------------------------

project = "intake_SDMX"
copyright = f"2020–{str(datetime.now().year)} intake_SDMX developers"
# The major project version, used as the replacement for |version|.
version = intake_sdmx.__version__[:3]
# The full project version, used as the replacement for |release|.
release = intake_sdmx.__version__


# -- General configuration ------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "IPython.sphinxext.ipython_console_highlighting",
    "IPython.sphinxext.ipython_directive",
]

# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = "alabaster"


# -- Options for sphinx.ext.intersphinx --------------------------------------

intersphinx_mapping = {
    "intake": ("https://intake.readthedocs.io/en/latest/", None),
    "sdmx": ("https://pandasdmx.readthedocs.io/en/latest/", None),
    "py": ("https://docs.python.org/3/", None),
    "requests": ("https://docs.python-requests.org/en/master/", None),
}


# -- Options for sphinx.ext.todo ---------------------------------------------

# If True, todo and todolist produce output, else they produce nothing.
todo_include_todos = True


# -- Options for IPython.sphinxext.ipython_directive -------------------------

# Specify if the embedded Sphinx shell should import Matplotlib and set the
# backend.
ipython_mplbackend = ""
