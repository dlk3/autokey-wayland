# AutoKey for Wayland Documentation

The [doumentation for this project](https://autokey-wayland.readthedocs.io) is published via [ReadtheDocs.org](https://readthedocs.org).

ReadtheDocs uses Sphinx to generate the AutoKey for Wayland documentation.  The documentation is automatically updated every time a change is pushed to the ```main``` branch of this repository.  No manual intervention is required, other than to verify the quality of the generated content.

Sphinx generates documentation for the scripting API modules in the ```lib/autokey/scripting``` directory based on reStructuredText docstrings that are included in those files. 

The rest of the documentation source is located here in this directory tree.  It is mostly composed as [reStructureText](https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html) files, but [Markdown](https://commonmark.org/) may also be used.

Configuration files:

- ```.readthedocs.yaml``` - Located in the root of this project.  Provides configuration for the ReadtheDocs builder.  [ReadtheDocs configuration file reference](https://docs.readthedocs.io/page/config-file/index.html).
- ```readthedocs/conf.py``` - Sphinx configuration file.  [Sphinx configuration file reference](https://www.sphinx-doc.org/en/master/usage/configuration.html).

