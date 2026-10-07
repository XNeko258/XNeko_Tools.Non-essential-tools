"""Stream cache management."""

import os
import hashlib
import tempfile
import bpy


AUDIO_EXT_CANDIDATES = (
    '.mp3', '.m4a', '.flac', '.ogg', '.wav', '.opus', '.aac', '.aiff',
)


def get_cache_dir():
    primary = os.path.join(os.path.dirname(__file__), '_cache')
    try:
        os.makedirs(primary, exist_ok=True)
        test = os.path.join(primary, '.write_test')
        with open(test, 'w') as f:
            f.write('')
        os.remove(test)
        return primary
    except OSError:
        fallback = os.path.join(tempfile.gettempdir(), 'xneko_music_cache')
        os.makedirs(fallback, exist_ok=True)
        return fallback


def _url_to_cache_name(url):
    digest = hashlib.md5(url.encode('utf-8')).hexdigest()
    ext = '.mp3'
    url_lower = url.lower()
    for candidate in AUDIO_EXT_CANDIDATES:
        if candidate in url_lower:
            ext = candidate
            break
    return digest + ext


def cache_path_for_url(url):
    return os.path.join(get_cache_dir(), _url_to_cache_name(url))


def cache_hit(url):
    path = cache_path_for_url(url)
    return os.path.exists(path) and os.path.getsize(path) > 1024


def get_cache_size_bytes():
    total = 0
    try:
        for f in os.listdir(get_cache_dir()):
            fp = os.path.join(get_cache_dir(), f)
            if os.path.isfile(fp):
                try:
                    total += os.path.getsize(fp)
                except OSError:
                    pass
    except OSError:
        pass
    return total


def get_cache_size_mb():
    return round(get_cache_size_bytes() / (1024 * 1024), 1)


def _get_prefs():
    try:
        pkg = __package__ or ""
        parts = pkg.split('.')
        for i in range(len(parts), 0, -1):
            name = '.'.join(parts[:i])
            if name in bpy.context.preferences.addons:
                prefs = bpy.context.preferences.addons[name].preferences
                if hasattr(prefs, 'xneko_music_cache_limit_mb'):
                    return prefs
    except Exception:
        pass
    for addon in bpy.context.preferences.addons.values():
        if hasattr(addon.preferences, 'xneko_music_cache_limit_mb'):
            return addon.preferences
    return None


def get_cache_limit_bytes():
    prefs = _get_prefs()
    limit_mb = 500
    if prefs is not None:
        try:
            limit_mb = int(prefs.xneko_music_cache_limit_mb)
        except Exception:
            pass
    return limit_mb * 1024 * 1024


def enforce_cache_limit():
    cache_dir = get_cache_dir()
    limit = get_cache_limit_bytes()

    files = []
    total = 0
    try:
        for f in os.listdir(cache_dir):
            fp = os.path.join(cache_dir, f)
            if os.path.isfile(fp):
                try:
                    st = os.stat(fp)
                    files.append((fp, st.st_mtime, st.st_size))
                    total += st.st_size
                except OSError:
                    pass
    except OSError:
        return 0

    if total <= limit:
        return 0

    files.sort(key=lambda x: x[1])
    deleted = 0
    for fp, _, size in files:
        if total <= limit:
            break
        try:
            os.remove(fp)
            total -= size
            deleted += 1
        except OSError:
            pass
    return deleted


def clear_all_cache():
    count = 0
    try:
        for f in os.listdir(get_cache_dir()):
            fp = os.path.join(get_cache_dir(), f)
            if os.path.isfile(fp):
                try:
                    os.remove(fp)
                    count += 1
                except OSError:
                    pass
    except OSError:
        pass
    return count