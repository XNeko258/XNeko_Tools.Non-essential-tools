"""N-panel UI (local files only)."""

import bpy

from . import _state
from ._timers import get_marquee_text


def _fmt_time(seconds):
    seconds = max(0, int(seconds))
    m, s = divmod(seconds, 60)
    return f"{m:02d}:{s:02d}"


def _shorten(text, limit=58):
    if not text:
        return ""
    if len(text) <= limit:
        return text
    return '...' + text[-(limit - 3):]


class VIEW3D_PT_xneko_music_player(bpy.types.Panel):
    bl_label = "Music Player"
    bl_idname = "VIEW3D_PT_xneko_music_player"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.prop(scene, "xneko_music_mode", text="")
        layout.separator()

        mode = scene.xneko_music_mode

        if mode == 'FILE':
            layout.prop(scene, "xneko_music_filepath", text="")

        elif mode == 'FOLDER':
            layout.prop(scene, "xneko_music_folder", text="")
            layout.operator("xneko.music_scan_folder", icon='FILE_REFRESH')
            if scene.xneko_music_playlist_count > 0:
                if scene.xneko_music_playlist_index < 0:
                    layout.label(text=f"{scene.xneko_music_playlist_count} track(s) loaded")
                else:
                    layout.label(
                        text=f"Track {scene.xneko_music_playlist_index + 1} / "
                             f"{scene.xneko_music_playlist_count}"
                    )
                row = layout.row(align=True)
                op = row.operator("xneko.music_playlist_step",
                                  text="Prev", icon='REW')
                if op is not None:
                    op.direction = -1
                op = row.operator("xneko.music_playlist_step",
                                  text="Next", icon='FF')
                if op is not None:
                    op.direction = 1

        # Title
        if scene.xneko_music_title:
            text = get_marquee_text(scene.xneko_music_title)
            layout.label(text=text, icon='SOUND')
        else:
            layout.label(text="No track loaded", icon='INFO')

        # Current path
        path = scene.xneko_music_current_path or scene.xneko_music_filepath
        if path:
            layout.label(text=_shorten(path), icon='FILE')

        # Playback controls
        is_playing = _state.is_playing
        
        row = layout.row(align=True)
        row.operator(
            "xneko.music_toggle",
            text="Pause" if is_playing else "Play",
            icon='PAUSE' if is_playing else 'PLAY',
        )
        row.operator("xneko.music_stop", text="Stop", icon='SNAP_FACE')
        
        # Prev / Next buttons on their own row
        if mode == 'FOLDER' and scene.xneko_music_playlist_count > 0:
            row = layout.row(align=True)
            op = row.operator("xneko.music_playlist_step",
                              text="Prev", icon='REW')
            if op is not None:
                op.direction = -1
            op = row.operator("xneko.music_playlist_step",
                              text="Next", icon='FF')
            if op is not None:
                op.direction = 1

        # Play mode
        row = layout.row(align=True)
        row.prop_enum(scene, "xneko_music_play_mode",
                      'SEQUENCE', icon='SORT_ASC', text="")
        row.prop_enum(scene, "xneko_music_play_mode",
                      'LOOP_ALL', icon='LOOP_BACK', text="")
        row.prop_enum(scene, "xneko_music_play_mode",
                      'LOOP_ONE', icon='FILE_REFRESH', text="")
        row.prop_enum(scene, "xneko_music_play_mode",
                      'SHUFFLE', icon='RNDCURVE', text="")

        # Time + jump buttons
        duration = scene.xneko_music_duration
        position = scene.xneko_music_position
        if duration > 0:
            layout.label(text=f"{_fmt_time(position)} / {_fmt_time(duration)}")
            row = layout.row(align=True)
            sub = row.row(align=True)
            sub.scale_x = 2.5
            op = sub.operator("xneko.music_jump", text="", icon='REW')
            if op is not None:
                op.direction = -1
            sub = row.row(align=True)
            sub.scale_x = 1.0
            sub.prop(scene, "xneko_music_jump_seconds", text="")
            sub = row.row(align=True)
            sub.scale_x = 2.5
            op = sub.operator("xneko.music_jump", text="", icon='FF')
            if op is not None:
                op.direction = 1
        else:
            layout.label(text="--:-- / --:--")

        layout.separator()
        layout.prop(scene, "xneko_music_volume", slider=True)

        if _state.is_playing:
            layout.label(text="Playing...", icon='SOUND')
        elif _state.handle is not None:
            layout.label(text="Paused", icon='PAUSE')

        # Playlist (Folder mode only)
        if mode == 'FOLDER' and len(scene.xneko_music_tracks) > 0:
            layout.separator()
            box = layout.box()
            box.label(
                text=f"Playlist ({len(scene.xneko_music_tracks)})",
                icon='PLAY',
            )
            box.template_list(
                "XNEKO_UL_music_playlist", "",
                scene, "xneko_music_tracks",
                scene, "xneko_music_tracks_index",
                rows=6,
            )


def draw_preferences(*args, **kwargs):
    """No-op stub for the addon preferences.

    The framework calls this with an unpredictable signature. Since the
    simplified local-only version has no settings to show, we simply
    do nothing to avoid noisy errors.
    """
    pass