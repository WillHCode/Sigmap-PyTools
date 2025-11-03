import sys
from pathlib import Path

# Add the src directory to the path so we can import the package
sys.path.insert(0, str(Path(__file__).parent.parent / "sigmap-pytools" / "src"))

# Read the version from pyproject.toml to ensure consistency
def get_version_from_pyproject():
    """Read version from pyproject.toml"""
    pyproject_path = Path(__file__).parent.parent / "sigmap-pytools" / "pyproject.toml"
    try:
        import tomllib
        with open(pyproject_path, 'rb') as f:
            data = tomllib.load(f)
        return data['project']['version']
    except (ImportError, KeyError, FileNotFoundError):
        import sigmap.polygeohasher
        return sigmap.polygeohasher.__version__

version = get_version_from_pyproject()
release = version

project = 'sigmap-pytools'
copyright = '2025, William Hubaux'
author = 'Hubaux William'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    'sphinx_autodoc_typehints',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_book_theme'
html_static_path = ['_static']

# Theme options for sphinx-book-theme
html_theme_options = {
    "repository_url": "https://github.com/WillHCode/Sigmap-PyTools",
    "use_repository_button": True,
    "use_edit_page_button": True,
    "use_issues_button": True,
    "path_to_docs": "docs",
    "use_download_button": True,
    "home_page_in_toc": True,
    "show_navbar_depth": 2,
    "show_toc_level": 2,
}

# -- Extension configuration -------------------------------------------------

# Napoleon settings for NumPy/Google style docstrings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True

# Autodoc settings
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': False,
    'show-inheritance': True,
}
autodoc_mock_imports = []

# Autosummary settings
autosummary_generate = True

# Intersphinx mapping
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'pandas': ('https://pandas.pydata.org/docs/', None),
    'geopandas': ('https://geopandas.org/', None),
    'shapely': ('https://shapely.readthedocs.io/en/stable/', None),
}

