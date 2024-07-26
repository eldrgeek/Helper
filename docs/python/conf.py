# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'MyProject'
copyright = '2024, Your Name'
author = 'Your Name'

version = '0.1'
release = '0.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

language = 'en'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']

# -- Requirements for Python packages -----------------------------------------
# Read requirements from requirements.txt
import os

# Adjust the path as necessary to point to your requirements.txt file
requirements_path = os.path.join(os.path.dirname(__file__), '..', '..', 'requirements.txt')

with open(requirements_path) as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

# You can now use the 'requirements' list in your Sphinx configuration
# For example, you might want to add it to the documentation:
html_context = {
    'project_dependencies': requirements
}

# If you want to categorize the requirements, you could do something like this:
main_dependencies = [
    'aiohttp', 'asyncio', 'netifaces', 'PyAutoGUI', 'python-socketio', 'requests'
]

html_context['main_dependencies'] = [req for req in requirements if any(req.startswith(dep) for dep in main_dependencies)]
html_context['other_dependencies'] = [req for req in requirements if req not in html_context['main_dependencies']]