"""Compatibility shim: provide moviepy.editor by re-exporting common symbols
from the installed moviepy package layout. This helps environments where
moviepy.editor is missing but moviepy.video.* exists.

This shim is only meant to satisfy imports from third-party libs like `fer`.
"""
try:
    from moviepy.video.io.VideoFileClip import VideoFileClip
    from moviepy.video.VideoClip import ImageClip
except Exception:
    # Best-effort fallback
    try:
        from moviepy.video.VideoClip import VideoClip as VideoFileClip
        from moviepy.video.VideoClip import VideoClip as ImageClip
    except Exception:
        VideoFileClip = None
        ImageClip = None

# Provide a minimal namespace so 'import moviepy.editor' can succeed
class _ShimModule:
    VideoFileClip = VideoFileClip
    ImageClip = ImageClip

shim = _ShimModule()

import sys
sys.modules.setdefault('moviepy.editor', shim)
