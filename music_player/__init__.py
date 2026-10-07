"""XNeko Tools - Music Player module (local files only)."""

import bpy

from ._deps import ensure_dependencies
ensure_dependencies()

from ._uilist import XNEKO_PG_music_track, XNEKO_UL_music_playlist, on_track_index_change
from ._audio import on_volume_change
from ._operators import (
    XNEKO_OT_music_play,
    XNEKO_OT_music_pause,
    XNEKO_OT_music_toggle,
    XNEKO_OT_music_stop,
    XNEKO_OT_music_jump,
    XNEKO_OT_music_advance,
    XNEKO_OT_music_scan_folder,
    XNEKO_OT_music_playlist_step,
    XNEKO_OT_music_playlist_jump,
)
from ._panels import VIEW3D_PT_xneko_music_player, draw_preferences


tool_id = "music_player"
tool_name = "Music Player"
tool_default_enabled = True
blender_version_min = (4, 0, 0)
group_icon = "SOUND"


def _on_mode_change(self, context):
    from . import _state
    from ._audio import stop_current
    from ._timers import _redraw_view3d

    stop_current()
    _state.current_path = ""
    _state.playlist_index = -1

    context.scene.xneko_music_position = 0.0
    context.scene.xneko_music_duration = 0.0
    context.scene.xneko_music_title = ""
    context.scene.xneko_music_current_path = ""
    context.scene.xneko_music_playlist_index = -1
    context.scene.xneko_music_tracks.clear()
    context.scene.xneko_music_tracks_index = 0

    _redraw_view3d()


scene_props = {
    "xneko_music_mode": bpy.props.EnumProperty(
        name="Input Mode",
        items=[
            ('FILE', "Single File", "Play a single audio file"),
            ('FOLDER', "Folder", "Scan a folder and pick tracks manually"),
        ],
        default='FILE',
        update=_on_mode_change,
    ),
    "xneko_music_filepath": bpy.props.StringProperty(
        name="Audio File", subtype='FILE_PATH', default="",
    ),
    "xneko_music_volume": bpy.props.FloatProperty(
        name="Volume", default=0.8, min=0.0, max=1.0,
        subtype='FACTOR', update=on_volume_change,
    ),
    "xneko_music_duration": bpy.props.FloatProperty(
        name="Duration", default=0.0, min=0.0,
    ),
    "xneko_music_position": bpy.props.FloatProperty(
        name="Position", default=0.0, min=0.0,
    ),
    "xneko_music_jump_seconds": bpy.props.IntProperty(
        name="Jump Seconds", default=10, min=1, max=600,
    ),
    "xneko_music_title": bpy.props.StringProperty(
        name="Title", default="",
    ),
    "xneko_music_folder": bpy.props.StringProperty(
        name="Music Folder", subtype='DIR_PATH', default="",
    ),
    "xneko_music_playlist_index": bpy.props.IntProperty(
        name="Playlist Index", default=-1, min=-1,
    ),
    "xneko_music_playlist_count": bpy.props.IntProperty(
        name="Playlist Count", default=0, min=0,
    ),
    "xneko_music_play_mode": bpy.props.EnumProperty(
        name="Play Mode",
        items=[
            ('SEQUENCE', "Sequence", "Play in order, stop after the last track", 'SORT_ASC', 0),
            ('LOOP_ALL', "Loop All", "Play in order, wrap to the first track", 'LOOP_BACK', 1),
            ('LOOP_ONE', "Loop One", "Repeat the current track", 'FILE_REFRESH', 2),
            ('SHUFFLE',  "Shuffle",  "Pick a random next track", 'RNDCURVE', 3),
        ],
        default='SEQUENCE',
    ),
    "xneko_music_tracks": bpy.props.CollectionProperty(type=XNEKO_PG_music_track),
    "xneko_music_tracks_index": bpy.props.IntProperty(
        name="Track Index", default=0, update=on_track_index_change,
    ),
    "xneko_music_current_path": bpy.props.StringProperty(
        name="Current Path", default="",
    ),
}


preference_props = {}


classes = (
    XNEKO_PG_music_track,
    XNEKO_UL_music_playlist,
    XNEKO_OT_music_play,
    XNEKO_OT_music_pause,
    XNEKO_OT_music_toggle, 
    XNEKO_OT_music_stop,
    XNEKO_OT_music_jump,
    XNEKO_OT_music_advance,
    XNEKO_OT_music_scan_folder,
    XNEKO_OT_music_playlist_step,
    XNEKO_OT_music_playlist_jump,
    VIEW3D_PT_xneko_music_player,
)