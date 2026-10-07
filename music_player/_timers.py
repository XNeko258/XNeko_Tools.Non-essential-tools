"""Timers - progress refresh, playback end detection, title marquee, redraw."""

import time
import bpy
import aud

from . import _state


MARQUEE_THRESHOLD = 20
MARQUEE_INTERVAL = 0.4
MARQUEE_PAUSE = 2


def _redraw_view3d():
    try:
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()
    except Exception:
        pass


def _do_advance():
    try:
        bpy.ops.xneko.music_advance()
    except Exception as e:
        print(f"[Music Player] Auto advance failed: {e}")


def check_playback_status():
    if _state.handle is None:
        return 1.0

    try:
        status = _state.handle.status
    except Exception:
        _state.handle = None
        _state.is_playing = False
        return 1.0

    if status == aud.STATUS_INVALID:
        _state.handle = None
        _state.is_playing = False
        try:
            bpy.context.scene.xneko_music_position = 0.0
        except Exception:
            pass
        _redraw_view3d()
        bpy.app.timers.register(_do_advance, first_interval=0.1)
        return 0.5

    if status == aud.STATUS_PLAYING:
        try:
            if time.time() - _state.last_seek_time > 0.5:
                scene = bpy.context.scene
                pos = float(_state.handle.position)
                scene.xneko_music_position = pos
        except Exception:
            pass
        _redraw_view3d()

    return 0.3


def ensure_timer_running():
    if not bpy.app.timers.is_registered(check_playback_status):
        bpy.app.timers.register(check_playback_status, first_interval=0.3)


def _tick_marquee():
    from . import _state

    now = time.time()
    if now - _state.marquee_last_tick < MARQUEE_INTERVAL:
        return MARQUEE_INTERVAL
    _state.marquee_last_tick = now

    try:
        title = bpy.context.scene.xneko_music_title
    except Exception:
        return MARQUEE_INTERVAL

    if not title or len(title) <= MARQUEE_THRESHOLD:
        _state.marquee_offset = 0
        _state.marquee_direction = 1
        _state.marquee_pause_ticks = 0
        return MARQUEE_INTERVAL

    max_offset = len(title) - MARQUEE_THRESHOLD
    if max_offset <= 0:
        return MARQUEE_INTERVAL

    if _state.marquee_pause_ticks > 0:
        _state.marquee_pause_ticks -= 1
        _redraw_view3d()
        return MARQUEE_INTERVAL

    _state.marquee_offset += _state.marquee_direction

    if _state.marquee_offset >= max_offset:
        _state.marquee_offset = max_offset
        _state.marquee_direction = -1
        _state.marquee_pause_ticks = MARQUEE_PAUSE
    elif _state.marquee_offset <= 0:
        _state.marquee_offset = 0
        _state.marquee_direction = 1
        _state.marquee_pause_ticks = MARQUEE_PAUSE

    _redraw_view3d()
    return MARQUEE_INTERVAL


def get_marquee_text(title):
    if not title:
        return ""
    if len(title) <= MARQUEE_THRESHOLD:
        return title
    offset = max(0, min(_state.marquee_offset, len(title) - MARQUEE_THRESHOLD))
    return title[offset:offset + MARQUEE_THRESHOLD]


def ensure_marquee_running():
    if not bpy.app.timers.is_registered(_tick_marquee):
        bpy.app.timers.register(_tick_marquee, first_interval=MARQUEE_INTERVAL)