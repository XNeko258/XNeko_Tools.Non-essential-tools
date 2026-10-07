"""All operators (local playback only)."""

import os
import random
import time
import bpy
import aud

from . import _state
from ._audio import stop_current, start_playback, ensure_device
from ._playlist import scan_audio_folder
from ._timers import (
    ensure_timer_running,
    ensure_marquee_running,
    _redraw_view3d,
)

from ._uilist import set_track_index


# ---------------------------------------------------------------
# Playback control
# ---------------------------------------------------------------

class XNEKO_OT_music_play(bpy.types.Operator):
    bl_idname = "xneko.music_play"
    bl_label = "Play"
    bl_description = "Play the currently selected audio file"
    bl_options = {'REGISTER'}

    def execute(self, context):
        scene = context.scene
        ensure_device()

        if scene.xneko_music_mode == 'FOLDER':
            return self._play_folder(context, scene)
        return self._play_file(context, scene)

    def _play_folder(self, context, scene):
        _ensure_playlist_synced(scene)

        if not _state.playlist:
            self.report({'WARNING'}, "Scan a folder first")
            return {'CANCELLED'}

        # Already playing -> do nothing
        if (_state.handle is not None and _state.is_playing):
            return {'FINISHED'}

        # Paused, and the current path matches the current list item -> resume
        can_resume = (
            _state.handle is not None
            and not _state.is_playing
            and 0 <= _state.playlist_index < len(_state.playlist)
            and _state.current_path == _state.playlist[_state.playlist_index]
        )
        if can_resume:
            _state.handle.resume()
            _state.is_playing = True
            _redraw_view3d()
            ensure_timer_running()
            ensure_marquee_running()
            return {'FINISHED'}

        # Pick a track to start
        play_mode = scene.xneko_music_play_mode
        if play_mode == 'SHUFFLE':
            idx = random.randint(0, len(_state.playlist) - 1)
        elif _state.playlist_index < 0:
            idx = 0
        else:
            idx = _state.playlist_index

        _state.playlist_index = idx
        scene.xneko_music_playlist_index = idx
        set_track_index(idx)

        filepath = _state.playlist[idx]
        scene.xneko_music_filepath = filepath
        start_playback(filepath, context)
        ensure_timer_running()
        ensure_marquee_running()
        return {'FINISHED'}

    def _play_file(self, context, scene):
        filepath = scene.xneko_music_filepath
        if not filepath:
            self.report({'ERROR'}, "Please select a valid audio file first")
            return {'CANCELLED'}

        abs_path = bpy.path.abspath(filepath)
        if not os.path.exists(abs_path):
            self.report({'ERROR'}, f"File does not exist: {abs_path}")
            return {'CANCELLED'}

        # Same file paused -> resume
        if (abs_path == _state.current_path
                and _state.handle is not None
                and not _state.is_playing):
            _state.handle.resume()
            _state.is_playing = True
            _redraw_view3d()
            ensure_timer_running()
            ensure_marquee_running()
            return {'FINISHED'}

        start_playback(abs_path, context)
        ensure_timer_running()
        ensure_marquee_running()
        return {'FINISHED'}
        

class XNEKO_OT_music_pause(bpy.types.Operator):
    bl_idname = "xneko.music_pause"
    bl_label = "Pause"
    bl_description = "Pause the current playback"
    bl_options = {'REGISTER'}

    def execute(self, context):
        if (_state.handle is not None
                and _state.handle.status == aud.STATUS_PLAYING):
            _state.handle.pause()
            _state.is_playing = False
            return {'FINISHED'}
        self.report({'INFO'}, "Nothing is currently playing")
        return {'CANCELLED'}


class XNEKO_OT_music_toggle(bpy.types.Operator):
    bl_idname = "xneko.music_toggle"
    bl_label = "Play / Pause"
    bl_description = "Toggle between play and pause"
    bl_options = {'REGISTER'}

    def execute(self, context):
        # Case 1: handle exists but paused -> resume
        if _state.handle is not None and not _state.is_playing:
            try:
                _state.handle.resume()
                _state.is_playing = True
                _redraw_view3d()
                ensure_timer_running()
                ensure_marquee_running()
                return {'FINISHED'}
            except Exception as e:
                print(f"[Music Player] Resume failed: {e}")

        # Case 2: currently playing -> pause
        if _state.handle is not None and _state.is_playing:
            try:
                _state.handle.pause()
                _state.is_playing = False
                _redraw_view3d()
                return {'FINISHED'}
            except Exception as e:
                print(f"[Music Player] Pause failed: {e}")

        # Case 3: no handle at all -> start from scratch
        return bpy.ops.xneko.music_play()


class XNEKO_OT_music_stop(bpy.types.Operator):
    bl_idname = "xneko.music_stop"
    bl_label = "Stop"
    bl_description = "Stop playback and reset the progress"
    bl_options = {'REGISTER'}

    def execute(self, context):
        stop_current()
        _state.current_path = ""
        context.scene.xneko_music_position = 0.0
        _redraw_view3d()
        return {'FINISHED'}


class XNEKO_OT_music_jump(bpy.types.Operator):
    bl_idname = "xneko.music_jump"
    bl_label = "Jump"
    bl_description = "Jump forward or backward by the configured seconds"
    bl_options = {'REGISTER'}

    direction: bpy.props.IntProperty(default=1)

    def execute(self, context):
        if _state.handle is None:
            self.report({'WARNING'}, "Nothing is playing")
            return {'CANCELLED'}

        try:
            duration = context.scene.xneko_music_duration
            current = float(_state.handle.position)
            step = context.scene.xneko_music_jump_seconds
            target = current + step * self.direction

            if target < 0:
                target = 0.0
            if duration > 0 and target > duration - 0.5:
                target = max(0.0, duration - 0.5)

            _state.handle.position = target
            _state.last_seek_time = time.time()

            context.scene.xneko_music_position = target
        except Exception as e:
            self.report({'ERROR'}, f"Jump failed: {e}")
            return {'CANCELLED'}

        return {'FINISHED'}


class XNEKO_OT_music_advance(bpy.types.Operator):
    bl_idname = "xneko.music_advance"
    bl_label = "Auto Advance"
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        mode = context.scene.xneko_music_mode
        play_mode = context.scene.xneko_music_play_mode

        if mode == 'FILE':
            if play_mode == 'LOOP_ONE':
                fp = context.scene.xneko_music_filepath
                if fp and os.path.exists(bpy.path.abspath(fp)):
                    start_playback(bpy.path.abspath(fp), context)
                    ensure_timer_running()
                    ensure_marquee_running()
            return {'FINISHED'}

        if mode == 'FOLDER':
            self._advance_folder(context, play_mode)
        return {'FINISHED'}

    def _pick_next(self, current, total, play_mode):
        if total <= 0:
            return None
        if play_mode == 'LOOP_ONE':
            return current
        if play_mode == 'SHUFFLE':
            if total == 1:
                return 0
            candidates = [i for i in range(total) if i != current]
            return random.choice(candidates)
        if play_mode == 'LOOP_ALL':
            return (current + 1) % total
        if current + 1 >= total:
            return None
        return current + 1

    def _advance_folder(self, context, play_mode):
        if not _state.playlist:
            return
        new_idx = self._pick_next(
            _state.playlist_index, len(_state.playlist), play_mode
        )
        if new_idx is None:
            return

        _state.playlist_index = new_idx
        context.scene.xneko_music_playlist_index = new_idx
        set_track_index(new_idx)

        filepath = _state.playlist[new_idx]
        context.scene.xneko_music_filepath = filepath
        start_playback(filepath, context)
        ensure_timer_running()
        ensure_marquee_running()


# ---------------------------------------------------------------
# Folder mode
# ---------------------------------------------------------------


def _ensure_playlist_synced(scene):
    """If _state.playlist is empty but the UIList has tracks, rebuild it.

    This handles the case where Blender reloads Python modules and wipes
    our module-level state while the UIList (a scene property) survives.
    """
    if not _state.playlist and len(scene.xneko_music_tracks) > 0:
        _state.playlist = [t.path for t in scene.xneko_music_tracks]


def _populate_tracks_from_folder(context, folder):
    tracks = context.scene.xneko_music_tracks
    tracks.clear()
    for i, path in enumerate(scan_audio_folder(folder)):
        item = tracks.add()
        item.index = i
        name = os.path.splitext(os.path.basename(path))[0]
        item.name = name[:50]
        item.path = path

    _state.suppress_uilist_click = True
    try:
        context.scene.xneko_music_tracks_index = 0
    finally:
        _state.suppress_uilist_click = False


class XNEKO_OT_music_scan_folder(bpy.types.Operator):
    bl_idname = "xneko.music_scan_folder"
    bl_label = "Scan Folder"
    bl_description = "Scan the selected folder for audio files"
    bl_options = {'REGISTER'}

    def execute(self, context):
        # Stop current playback and clear old state
        stop_current()
        _state.current_path = ""
        _state.playlist_index = -1

        folder = bpy.path.abspath(context.scene.xneko_music_folder)
        result = scan_audio_folder(folder)
        _state.playlist = result

        context.scene.xneko_music_playlist_count = len(result)
        context.scene.xneko_music_playlist_index = -1
        context.scene.xneko_music_position = 0.0
        context.scene.xneko_music_duration = 0.0
        context.scene.xneko_music_title = ""
        context.scene.xneko_music_current_path = ""

        _populate_tracks_from_folder(context, folder)

        if not result:
            self.report({'WARNING'}, "No audio files found in this folder")
            return {'CANCELLED'}
        self.report({'INFO'}, f"Found {len(result)} track(s)")
        return {'FINISHED'}


class XNEKO_OT_music_playlist_step(bpy.types.Operator):
    bl_idname = "xneko.music_playlist_step"
    bl_label = "Step Track"
    bl_options = {'REGISTER'}

    direction: bpy.props.IntProperty(default=1)

    def execute(self, context):
        _ensure_playlist_synced(context.scene)

        if not _state.playlist:
            self.report({'WARNING'}, "Scan a folder first")
            return {'CANCELLED'}

        n = len(_state.playlist)
        play_mode = context.scene.xneko_music_play_mode

        if play_mode == 'SHUFFLE' and n > 1:
            candidates = [i for i in range(n) if i != _state.playlist_index]
            idx = random.choice(candidates)
        else:
            idx = _state.playlist_index + self.direction
            if idx >= n:
                idx = 0
            elif idx < 0:
                idx = n - 1

        _state.playlist_index = idx
        context.scene.xneko_music_playlist_index = idx
        set_track_index(idx)

        filepath = _state.playlist[idx]
        context.scene.xneko_music_filepath = filepath

        ensure_device()
        start_playback(filepath, context)
        ensure_timer_running()
        ensure_marquee_running()
        return {'FINISHED'}


class XNEKO_OT_music_playlist_jump(bpy.types.Operator):
    bl_idname = "xneko.music_playlist_jump"
    bl_label = "Jump to Track"
    bl_options = {'REGISTER'}

    index: bpy.props.IntProperty(default=0)

    def execute(self, context):
        _ensure_playlist_synced(context.scene)

        if not _state.playlist:
            return {'CANCELLED'}
        if not (0 <= self.index < len(_state.playlist)):
            return {'CANCELLED'}

        _state.playlist_index = self.index
        context.scene.xneko_music_playlist_index = self.index
        set_track_index(self.index)

        filepath = _state.playlist[self.index]
        context.scene.xneko_music_filepath = filepath

        ensure_device()
        start_playback(filepath, context)
        ensure_timer_running()
        ensure_marquee_running()
        return {'FINISHED'}