"""Stream buffering and cache reuse."""

import os
import threading
import urllib.request
import bpy

from . import _state
from ._cache import cache_path_for_url, cache_hit, enforce_cache_limit
from ._audio import start_playback


def _schedule_update(attr, value):
    def _apply():
        try:
            setattr(bpy.context.scene, attr, value)
        except Exception:
            pass
    bpy.app.timers.register(_apply, first_interval=0)


def _open_url(url, timeout=30):
    req = urllib.request.Request(
        url,
        headers={
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/120.0.0.0 Safari/537.36'
            ),
            'Accept': '*/*',
        },
    )
    return urllib.request.urlopen(req, timeout=timeout)


def buffer_and_play(url, title, context):
    cache_path = cache_path_for_url(url)

    if cache_hit(url):
        context.scene.xneko_music_is_buffering = False
        context.scene.xneko_music_buffer_progress = 1.0
        try:
            os.utime(cache_path, None)
        except OSError:
            pass
        start_playback(cache_path, context)
        context.scene.xneko_music_current_path = url
        return

    _state.stream_stop_flag = True
    if _state.stream_buffer_thread and _state.stream_buffer_thread.is_alive():
        _state.stream_buffer_thread.join(timeout=2)
    _state.stream_stop_flag = False
    _state.stream_current_url = url

    context.scene.xneko_music_is_buffering = True
    context.scene.xneko_music_buffer_progress = 0.0
    context.scene.xneko_music_title = title
    context.scene.xneko_music_duration = 0.0
    context.scene.xneko_music_position = 0.0
    context.scene.xneko_music_current_path = url

    def worker():
        try:
            with _open_url(url) as resp:
                total_size = int(resp.headers.get('Content-Length', 0) or 0)
                downloaded = 0
                with open(cache_path, 'wb') as f:
                    while not _state.stream_stop_flag:
                        chunk = resp.read(16384)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            _schedule_update(
                                'xneko_music_buffer_progress',
                                downloaded / total_size,
                            )

            if _state.stream_stop_flag:
                try:
                    os.remove(cache_path)
                except OSError:
                    pass
                return

            def done():
                try:
                    sc = bpy.context.scene
                    sc.xneko_music_is_buffering = False
                    sc.xneko_music_buffer_progress = 1.0
                    enforce_cache_limit()
                    start_playback(cache_path, sc)
                    sc.xneko_music_current_path = url
                except Exception as e:
                    print(f"[Music Player] Buffer done callback failed: {e}")
            bpy.app.timers.register(done, first_interval=0.1)

        except Exception as e:
            print(f"[Music Player] Buffering failed: {e}")
            try:
                if os.path.exists(cache_path):
                    os.remove(cache_path)
            except OSError:
                pass
            _schedule_update('xneko_music_is_buffering', False)

    _state.stream_buffer_thread = threading.Thread(target=worker, daemon=True)
    _state.stream_buffer_thread.start()


def stop_stream():
    _state.stream_stop_flag = True
    if _state.stream_buffer_thread and _state.stream_buffer_thread.is_alive():
        _state.stream_buffer_thread.join(timeout=1.5)
    _state.stream_buffer_thread = None