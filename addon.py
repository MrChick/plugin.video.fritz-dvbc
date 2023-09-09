import sys
import urllib.error

import m3u8
import xbmcplugin as plugin
from xbmcgui import ListItem, Dialog


# filter out #EXTVLCOPT lines in the M3U files to circumvent a bug in m3u8 < 3.6.0
def drop_extvlcopt(line, lineno, data, state):
    if line.startswith('#EXTVLCOPT'):
        return True
    else:
        return False


def get_available_channels():
    hostname = plugin.getSetting(addon_handle, 'host')
    sources = []

    if plugin.getSetting(addon_handle, 'tvsd') == 'true':
        sources.append(f"http://{hostname}/dvb/m3u/tvsd.m3u")

    if plugin.getSetting(addon_handle, 'tvhd') == 'true':
        sources.append(f"http://{hostname}/dvb/m3u/tvhd.m3u")

    channels = []
    try:
        for source in sources:
            for stream in m3u8.load(source, custom_tags_parser=drop_extvlcopt).segments:
                channels.append(dict(title=stream.title, uri=stream.uri))
    except urllib.error.URLError as e:
        Dialog().ok("Error", str(e))

    return channels


addon_handle = int(sys.argv[1])
plugin.setContent(addon_handle, 'videos')

for available_channel in get_available_channels():
    channel = ListItem(label=available_channel['title'])
    channel.setInfo('video', {'title': available_channel['title']})
    plugin.addDirectoryItem(handle=addon_handle, url=available_channel['uri'], listitem=channel)

plugin.addSortMethod(addon_handle, plugin.SORT_METHOD_TITLE)
plugin.endOfDirectory(addon_handle)
