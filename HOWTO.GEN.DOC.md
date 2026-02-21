# How to produce the contents of the doc folder

The scripting modules are commented with docstrings containing reStructuredText markup.

Originally, [Epydoc](https://epydoc.sourceforge.net/) was used to format these comments into HTML documents.  As of this writing, Epydoc has been replaced by pydoctor.

This command can be used to generate the content for the ```doc/scripting``` folder:
```
pydoctor --docformat=restructuredtext --project-name="AutoKey Script" --project-version=0.97.2 --project-url=https://github.com/dlk3/autokey-wayland --html-viewsource-base=https://github.com/dlk3/autokey-wayland/tree/v0.97.2 --html-output=doc/scripting lib/autokey/scripting/*
```



