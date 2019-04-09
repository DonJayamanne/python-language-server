try:
	import ptvsd
	ptvsd.enable_attach()
	ptvsd.wait_for_attach()
except Exception:
	pass


# Copyright 2017 Palantir Technologies, Inc.
import os
from future.standard_library import install_aliases
import pluggy
from ._version import get_versions

install_aliases()
__version__ = get_versions()['version']
del get_versions

PYLS = 'pyls'

hookspec = pluggy.HookspecMarker(PYLS)
hookimpl = pluggy.HookimplMarker(PYLS)

IS_WIN = os.name == 'nt'
