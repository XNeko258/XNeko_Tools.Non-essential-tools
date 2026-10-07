"""Shared mutable state across all submodules."""

device = None
handle = None
current_path = ""
is_playing = False

playlist = []
playlist_index = -1

marquee_offset = 0
marquee_direction = 1
marquee_pause_ticks = 0
marquee_last_tick = 0.0

suppress_uilist_click = False
last_seek_time = 0.0