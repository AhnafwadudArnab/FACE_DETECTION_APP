import sys
from pathlib import Path
# Ensure local webapp shim is importable
sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    # load the shim so fer's import moviepy.editor works
    import moviepy_editor_shim  # noqa: F401
except Exception:
    pass
try:
    import fer
    print('fer available, version =', getattr(fer, '__version__', 'unknown'))
except Exception as e:
    print('fer import error:', e)
