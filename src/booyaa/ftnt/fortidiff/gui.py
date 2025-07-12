import wx
import os

try:
    from fortidiff import core
except:
    import os, sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
    from fortidiff import core
finally:
    pass

