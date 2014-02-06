import cookielib
import HTMLParser
import json
import os
import sys
import urllib
import urllib2
import urlparse
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmcvfs

class ListParser(HTMLParser.HTMLParser):
	addvideos = False
	def handle_starttag(self, tag, attrs):
		try:
			attrs = dict(attrs)
			href = attrs['href']
			if self.addvideos and 'class' in attrs and attrs['class'] == 'uniblue':
				nodepath = href.rpartition('/')[2]
				label = nodepath
				isFolder = False
			else:
				query = urlparse.parse_qs(urlparse.urlparse(href).query)
				nodepath = query['nodepath'][0].encode('latin')
				self.addvideos = nodepath == pluginurl.path
				label = nodepath.partition(pluginurl.path)[2].strip('/')
				isFolder = True
				if label == "" or "/" in label:
					return
			url = urlparse.urlunparse((pluginurl.scheme, pluginurl.netloc, nodepath, "", "", ""))
			listitem = xbmcgui.ListItem(label)
			xbmcplugin.addDirectoryItem(addon_handle, url, listitem, isFolder)
		except (IndexError, KeyError):
			pass

pluginurl = urlparse.urlparse(sys.argv[0])
addon = xbmcaddon.Addon(id=pluginurl.netloc)
profile = addon.getAddonInfo("profile")
profilepath = xbmc.translatePath(profile)
cookiefilename = os.path.join(profilepath, "cookies.txt")
cookiejar = cookielib.LWPCookieJar(cookiefilename)
try:
	cookiejar.load(ignore_discard=True)
except:
	xbmcvfs.mkdir(profilepath)

urlopener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar))
url = "http://timmsrc.uni-tuebingen.de/"
addon_handle = int(sys.argv[1])
if addon_handle == -1:
	url += "Player/GetLocations/" + pluginurl.path
	f = urlopener.open(url)
	locations = json.load(f)
	xbmc.Player().play(locations['Wmvs'][-1]['href'])
else:
	url += "List/OpenNode?" + urllib.urlencode({'nodepath':pluginurl.path})
	f = urlopener.open(url)
	ListParser().feed(f.read())
	xbmcplugin.endOfDirectory(addon_handle)

f.close()
cookiejar.save(ignore_discard=True)
