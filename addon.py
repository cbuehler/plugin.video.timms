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
	gettitle = False
	nodepath = None
	isFolder = True
	thumbnailImage = None
	listitem = xbmcgui.ListItem()

	def handle_starttag(self, tag, attrs):
		try:
			attrs = dict(attrs)
			try:
				self.thumbnailImage = attrs['src']
			except KeyError:
				pass
			href = attrs['href']
			if self.addvideos and 'class' in attrs and attrs['class'] == 'uniblue':
				self.nodepath = href.rpartition('/')[2]
				self.isFolder = False
				self.gettitle = True
				self.listitem.setThumbnailImage(self.thumbnailImage)
			else:
				query = urlparse.parse_qs(urlparse.urlparse(href).query)
				self.nodepath = query['nodepath'][0].encode('latin')
				self.addvideos = self.nodepath == pluginurl.path
				self.isFolder = True
				label = self.nodepath.partition(pluginurl.path)[2].strip('/')
				if label != "" and "/" not in label:
					self.listitem.setLabel(label)
		except (IndexError, KeyError):
			pass

	def handle_endtag(self, tag):
		if not self.listitem.getLabel():
			return
		url = urlparse.urlunparse((pluginurl.scheme, pluginurl.netloc, self.nodepath, "", "", ""))
		xbmcplugin.addDirectoryItem(addon_handle, url, self.listitem, self.isFolder)
		self.listitem = xbmcgui.ListItem()
		self.gettitle = False

	def addtolabel(self, data):
		label = self.listitem.getLabel()
		label += data
		self.listitem.setLabel(label)

	def handle_data(self, data):
		if not self.gettitle:
			return
		self.addtolabel(data)

	def handle_charref(self, name):
		if not self.gettitle:
			return
		c = unichr(int(name)).encode('utf-8')
		self.addtolabel(c)

pluginurl = urlparse.urlparse(sys.argv[0])
addon = xbmcaddon.Addon()
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
