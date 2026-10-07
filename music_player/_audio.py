"""Audio backend - aud wrapper plus mutagen metadata."""

import os
import time
import bpy
import aud

from . import _state


def read_audio_info(filepath):
    duration = 0.0
    title = os.path.splitext(os.path.basename(filepath))[0]

    try:
        from mutagen import File as MutagenFile
        audio = MutagenFile(filepath)
        if audio is not None:
            if hasattr(audio, 'info') and hasattr(audio.info, 'length'):
                duration = float(audio.info.length)
            if hasattr(audio, 'tags') and audio.tags:
                for key in ('TIT2', 'title', 'TITLE', '\xa9nam'):
                    try:
                        if key in audio.tags:
                            val = audio.tags[key]
                            if isinstance(val, list) and val:
                                title = str(val[0])
                            else:
                                title = str(val)
                            break
                    except Exception:
                        continue
    except Exception as e:
        print(f"[Music Player] Failed to read audio info: {e}")

    return duration, title


def ensure_device():
    if _state.device is None:
        _state.device = aud.Device()
    return _state.device


def stop_current():
    if _state.handle is not None:
        try:
            _state.handle.stop()
        except Exception:
            pass
    _state.handle = None
    _state.is_playing = False


def start_playback(filepath, context):
    device = ensure_device()
    stop_current()

    _state.current_path = filepath
    _state.handle = device.play(aud.Sound(filepath))
    _state.handle.volume = context.scene.xneko_music_volume
    _state.is_playing = True

    duration, title = read_audio_info(filepath)
    context.scene.xneko_music_duration = duration
    context.scene.xneko_music_title = title
    context.scene.xneko_music_position = 0.0
    context.scene.xneko_music_current_path = filepath

    _state.marquee_offset = 0
    _state.marquee_direction = 1
    _state.marquee_pause_ticks = 2
    _state.marquee_last_tick = 0.0


def on_volume_change(self, context):
    if _state.handle is not None:
        try:
            _state.handle.volume = self.xneko_music_volume
        except Exception:
            pass