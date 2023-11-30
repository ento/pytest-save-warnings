try:
    from ._version import (  # pyright: ignore [reportMissingImports]
        __version__,  # pyright: ignore [reportUnknownVariableType]
    )
except ImportError:
    __version__ = "0+unknown"
