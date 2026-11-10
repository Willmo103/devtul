"""
DevTul - A collection of developer tools for working with git repositories.
"""

try:
    from .main import __version__, app, main

    __all__ = ["app", "main", "__version__"]
except ImportError:
    try:
        from importlib.metadata import version as _pkg_version

        __version__ = _pkg_version("devtul")
    except Exception:
        __version__ = "0.7.0"

    app = None
    main = None
    __all__ = ["__version__"]
