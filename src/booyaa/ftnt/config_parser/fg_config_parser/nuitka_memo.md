


python -m nuitka --standalone --follow-imports --assume-yes-for-downloads fg_config_parser_gui.py

```ps
$ python -m nuitka --plugin-list 
                 The following plugins are available in Nuitka
--------------------------------------------------------------------------------
 anti-bloat        Patch stupid imports out of widely used library modules source codes.
 data-files        Include data files specified by package configuration files.
 delvewheel        Required for 'support' of delvewheel using packages in standalone mode.
 dill-compat       Required for 'dill' package compatibility.
 dll-files         Include DLLs as per package configuration files.
 enum-compat       Required for Python2 and 'enum' package.
 eventlet          Support for including 'eventlet' dependencies and its need for 'dns' package monkey patching.
 gevent            Required by the 'gevent' package.
 gi                Support for GI package typelib dependency.
 glfw              Required for OpenGL and 'glfw' package in standalone mode.
 implicit-imports  Provide implicit imports of package as per package configuration files.
 kivy              Required by 'kivy' package.
 matplotlib        Required for 'matplotlib' module.
 multiprocessing   Required by Python's 'multiprocessing' module.
 no-qt             Disable all Qt bindings for standalone mode.
 options-nanny     Inform the user about potential problems as per package configuration files.
 pbr-compat        Required by the 'pbr' package in standalone mode.
 pkg-resources     Workarounds for 'pkg_resources'.
 pmw-freezer       Required by the 'Pmw' package.
 pylint-warnings   Support PyLint / PyDev linting source markers.
 pyqt5             Required by the PyQt5 package.
 pyqt6             Required by the PyQt6 package for standalone mode.
 pyside2           Required by the PySide2 package.
 pyside6           Required by the PySide6 package for standalone mode.
 pywebview         Required by the 'webview' package (pywebview on PyPI).
 tk-inter          Required by Python's Tk modules.
 transformers      Provide implicit imports for transformers package.
 upx               Compress created binaries with UPX automatically.
 ```
