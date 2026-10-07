"""UIList playlist, PropertyGroup and index callback."""

import bpy

from . import _state


def set_track_index(idx):
    _state.suppress_uilist_click = True
    try:
        bpy.context.scene.xneko_music_tracks_index = idx
    except Exception:
        pass
    _state.suppress_uilist_click = False


def on_track_index_change(self, context):
    if _state.suppress_uilist_click:
        return

    idx = self.xneko_music_tracks_index
    if self.xneko_music_mode == 'FOLDER':
        try:
            bpy.ops.xneko.music_playlist_jump(index=idx)
        except Exception:
            pass


class XNEKO_PG_music_track(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Name", default="")
    path: bpy.props.StringProperty(name="Path", default="")
    index: bpy.props.IntProperty(name="Index", default=0)


class XNEKO_UL_music_playlist(bpy.types.UIList):
    bl_idname = "XNEKO_UL_music_playlist"

    def draw_item(self, context, layout, data, item, icon,
                  active_data, active_propname, index):
        layout.label(
            text=f"{index + 1}. {item.name or 'Untitled'}",
            icon='SOUND',
        )