#!/usr/bin/python
# RhythmDesk 
# developed by jurgo boemo 
#tanks to:
# 	Sebastian Lara Menares (developer of deskbar-rhytmbox)
# 	Darshan Shaligram <scintilla@gmail.com> (developer of deskbar-exaile)
#	Jordi hernandez (developer of CoverGloobus)
#	all Rhythmbox team

from xml.etree.ElementTree import parse
import dbus
import os.path
import deskbar
import deskbar.interfaces.Module
import deskbar.interfaces.Match
import deskbar.interfaces.Action
import deskbar.core.Utils
import sys
import os
import pygtk
pygtk.require('2.0')
import gtk
import urllib
import re
import gtk
import cairo
from gtk import gdk
import threading
import commands
import os.path
from deskbar.handlers.actions.OpenWithApplicationAction import OpenWithApplicationAction

#from deskbar.handlers.actions.OpenWithApplicationAction import OpenWithApplicationAction
from deskbar.handlers.actions.ShowUrlAction import ShowUrlAction



class Lyrics:
	song 	= ""
	win 	= None
	
	def create_window(self):
			self.win = gtk.Window()
			self.win.set_title('Lyrics')
			self.win.stick()		
			self.win.set_default_size(self.get_width(), self.get_height())				#All desktops
		 	#win.set_keep_below(True)													#Keep the window below the others
			self.win.set_decorated(False)												#No Decoration
			self.win.set_property("skip-taskbar-hint", True)							#No Deskbar Entry

				#win.connect('delete-event', gtk.main_quit)
			self.win.set_app_paintable(True)
			self.win.connect('expose-event',	self.expose)
			self.win.add_events(gdk.KEY_PRESS_MASK|gdk.KEY_RELEASE_MASK|gdk.BUTTON_PRESS_MASK)			
			self.win.connect("key-press-event",self.on_win_key_press_event )
		
			self.win.connect('button-press-event', self.clicked)
		 
			self.win.set_colormap( self.win.get_screen().get_rgba_colormap())						#Set Alpha Screen
			self.win.show_all()
	
	def on_win_key_press_event(self, widget, event):
		print "tasto"
		key = gtk.gdk.keyval_name(event.keyval)
		if key == "Escape" or key == "q":		
			self.win.destroy()
			gtk.main_quit()


	def expose(self, widget, event):
		(width, height) = widget.get_size()			 	#Get window size
		cr = widget.window.cairo_create()				#Get a cairo context
		cr.set_source_rgba(1.0, 1.0, 1.0, 0.0)			#Make the window transparent
		cr.set_operator(cairo.OPERATOR_SOURCE)			#Make the window transparent
		cr.paint()										#Make the window transparent
		cr.set_operator(cairo.OPERATOR_OVER);
		self.cr=cr
		self.draw_background(cr,width,height)	 	#Draw the nice background
		self.draw_lyrics(cr)
		
		return False

	def draw_background(self, cr, w, h):
		x = 0
		y = 0
		r = 15
		cr.set_operator(cairo.OPERATOR_OVER);
		cr.set_source_rgba (0, 0, 0, 0.8);			# Background opacity		
		cr.move_to	( x+r,y )								# Move to A
		cr.line_to	( x+w-r,y )								# Straight line to B
		cr.curve_to	( x+w-r,y,x+w,y,x+w,y+r )		# Curve to C
		cr.line_to	( x+w,y+h-r )					 	# Move to D
		cr.curve_to	( x+w,y+h-r,x+w,y+h,x+w-r,y+h )	# Curve to E
		cr.line_to	( x+r,y+h )							# Line to F
		cr.curve_to	( x+r,y+h,x,y+h,x,y+h-r )		# Curve to G
		cr.line_to	( x,y+r )							 	# Line to H
		cr.curve_to	( x,y+r,x,y,x+r,y)				# Curve to G
		cr.fill		( )	 

	def draw_lyrics(self,cr):
		cr.save()

		cr.move_to(20,20)
		cr.select_font_face("Lucida Grande", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
		cr.set_font_size(12)
		y = 20
		x=20
		i=0
		if self.song == "":
			self.song="Searching:\n\n Wait \nplease...\n\n"	
		for line in self.song.splitlines():
			#cr.move_to(19,y)						#Shadow
			#cr.set_source_rgba(0.0, 0.0, 0.0,0.9)	#Shadow
			#cr.show_text(unicode(line, "utf-8"))	#Shadow
			if(i==len(self.song.splitlines())/2) :
				x=self.get_width()/2
				y=60
			
			cr.move_to(x,y)						#Normal
			cr.set_source_rgb(1.0, 1.0, 1.0)		#Normal
			cr.show_text(unicode(line, "utf-8"))	#Normal
			y = y + 15
			i+=1
		cr.restore()
	def get_height(self):
		MAX_LEN=11200
		if self.song == "":
			return 100
		else:
			res=int(	(self.song.count("\n")*17) /2	+30)
			if res > MAX_LEN:
				res=MAX_LEN	
			return res


	def	get_width(self):
		if self.song == "":
			return 170
		else:
			size = 0
			for line in self.song.splitlines():
				if len(line) > size:
					size = len(line)
			if size > 200:
				size=200
			return size *2* 8				#Need to find this value
	
	def clicked(self,widget, event):
		if event.button == 2:
			self.win.destroy()
			gtk.main_quit()
		else:
			self.win.begin_move_drag(event.button, int(event.x_root), int(event.y_root), event.time)







class AsyncSearch(threading.Thread):
	
	stopthread = threading.Event()	
	def __init__(self, window, artist, title):
		threading.Thread.__init__(self)			
		self.window=window		
		self.artist=unicode(artist)
		self.title=unicode(title)
		
	def run(self, ):
		l = GetLyrics()
		self.lyric =	l.get_song_lyricwiki(self.artist, self.title)				
		gdk.threads_enter()
		self.window.win.destroy()		
		gdk.threads_leave()
		gtk.main_quit()


	def stop(self):
		"""Stop method, sets the event to terminate the thread's main loop"""
		self.stopthread.set()
		print "quit main"

class GetLyrics:
	def get_song_lyricwiki(self, artist, song):	
		artist_name = artist.replace(" ","_")
		song_name = song.replace(" ","_")
		URL = "http://lyricwiki.org/" + artist_name + ":" + song_name
		print URL
		web = urllib.urlopen(URL)
		web_code = web.read()
		regexp = re.compile ("<div class='lyricbox' >(.*)<p>",re.DOTALL)
		m = re.search(regexp, web_code)
		if m:		
			lyric = m.group(1).replace("<br />", "\n")
			lyric=unicode(lyric)			
			print lyric		
			#song = unicode.encode(song) +"\n" + unicode.encode(artist) + "\n\n" + lyric
		else:
			lyric = unicode.encode(unicode("No Lyrics for this song found\n"))
		return lyric







###############################################
##						PLUGIN						###
###############################################



USED_PLAYER=commands.getoutput( "cat ~/.gconf/desktop/gnome/applications/media/%gconf.xml |egrep '<stringvalue>'|sed s/'<stringvalue>'//g|sed s/'<\/stringvalue>'//g|tr -d '\t'" )

#USED_PLAYER="exaile"
MAX_RESULTS=1000

if USED_PLAYER!="rhythmbox" and USED_PLAYER!="exaile":
	print "player "+USED_PLAYER+"is not supported"


##sendto
class SendToAction(OpenWithApplicationAction):
    
    def __init__(self, song, artist, uri):
        OpenWithApplicationAction.__init__(self, song, "nautilus-sendto", [uri])
        self._song = song
        self._artist = artist
    
    def get_icon(self):
        return "stock_edit"
    
    def get_name(self, text=None):
        return {
            "song": self._song,
            "artist": self._artist,
        }
    
    def get_verb(self):
        #translators: First %s is the contact full name, second %s is the email address
        return "Send song <b>"+self._song+"</b> by ("+self._artist+')'





##lyrics
class DeskRhythmLyricAction(deskbar.interfaces.Action):
	 def __init__(self, song,artist,album):
			deskbar.interfaces.Action.__init__(self, song)		
			self._song = song
			self._artist = artist
			self._album	= album
	 def activate(self,text=None):
			artist=unicode(self._artist)
			title=unicode(self._song)		
			wait_win = Lyrics()
			search=AsyncSearch(wait_win,artist ,title )
			gtk.gdk.threads_init()
			search.start()
			wait_win.create_window()
			gtk.main()
			search.stop()
			lyric_win=Lyrics()
			lyric_win.song= str(artist)+"\n"+str(title)+"\n\n"+	str(search.lyric)
			lyric_win.create_window()
			gtk.main()
	 def get_verb(self):
			out = 'Lyric of <b>%(name)s</b>\n by <i>'+self._artist+'</i> from <i>'+self._album+'</i>'
			return out
	 def get_hash(self, text=None):
			return "lyric"+self._song+self._artist+self._album

##last.fm
class SearchLastFMAction(ShowUrlAction):
	def __init__(self,song, artist, album):
		self._song = song
		self._artist = artist
		self._album	= album	
		self._url = self.create_url()		
		ShowUrlAction.__init__(self, "", self._url)
	def get_verb(self):
		#translators: First %s is the contact full name, second %s is the email address
		return "Search on Last.fm <b>"+self._song+'</b> \n by <i>'+self._artist+'</i>' 
	def create_url(self):
		return "http://www.last.fm/search?q="+self._artist+"+"+self._song+"&m=music"

##libre.fm
class SearchLibreFMAction(ShowUrlAction):
	def __init__(self,song, artist, album):
		self._song = song
		self._artist = artist
		self._album	= album	
		self._url = self.create_url()		
		ShowUrlAction.__init__(self, "", self._url)
	def get_verb(self):
		#translators: First %s is the contact full name, second %s is the email address
		return "Search on Libre.fm <b>"+self._song+'</b> \n by <i>'+self._artist+'</i>' 
	def create_url(self):
		return "http://alpha.libre.fm/artist/"+self._artist+"/track/"+self._song







################################################
##various class                               ##
################################################


##rhythmbox
if USED_PLAYER=="rhythmbox":
	if USED_PLAYER=="rhythmbox":
		
		RB_DB_PATH='.local/share/rhythmbox/rhythmdb.xml'
		filename = os.path.join(os.path.expanduser('~'),RB_DB_PATH)
		tree = parse(filename)
		songs = tree.getroot().findall("entry")
		HANDLERS = ["DeskRhythmHandler"]
		bus = dbus.SessionBus()

	#variuos play Actions
	class DeskRhythmAction(deskbar.interfaces.Action):
		def __init__(self, song,uri,artist,album):
			deskbar.interfaces.Action.__init__(self, song)
			self._song = song
			self._uri = uri
			self._artist = artist
			self._album	= album

		def activate(self,text=None):
			proxy_obj = bus.get_object( 'org.gnome.Rhythmbox','/org/gnome/Rhythmbox/Shell')
			player = dbus.Interface(proxy_obj, 'org.gnome.Rhythmbox.Shell')
			player.loadURI(dbus.String(self._uri), True)
			
		def get_verb(self):
			out = 'Play <b>%(name)s</b>\n by <i>'+self._artist+'</i> from <i>'+self._album+'</i>'
			return out

		def get_hash(self, text=None):
			return "play"+self._song+self._artist+self._album

	if USED_PLAYER=="rhythmbox":
		class DeskRhythmActionSon(DeskRhythmAction):
			def __(self, song,uri,artist,album):
				DeskRhythmAction.__init__(self, song,uri,artist,album)



	
	class DeskRhythmMatch(deskbar.interfaces.Match):
		 def __init__(self, song,uri,artist,album, **kwargs):
				deskbar.interfaces.Match.__init__(	self, 
																song=None, uri=None,artist=None,album=None, 
																icon='audio-x-generic', 
																category='actions', 
																**kwargs)
				self.song = song
				self.uri = uri
				self.artist = artist
				self.album = album

				self.add_action( DeskRhythmActionSon(self.song,self.uri,self.artist,self.album), True)
				self.add_action( DeskRhythmLyricAction(self.song,self.artist,self.album))
				self.add_action( SearchLastFMAction(self.song,self.artist,self.album))
				self.add_action( SearchLibreFMAction(self.song,self.artist,self.album))
				self.add_action(SendToAction(self.song, self.artist, self.uri) )


		 def get_hash(self, text=None):
				return "match"+self.song+self.artist+self.album







	class DeskRhythmHandler(deskbar.interfaces.Module):
		 INFOS = {	'icon':		deskbar.core.Utils.load_icon('audio-x-generic'),
						 'name':		'RhythmDesk',
						 'description':	'Search and change Rhythmbox playing song, get lyrics, search info, send yout music',
						 'version':		'0.0.9'
		 }

		 def __init__(self):
				deskbar.interfaces.Module.__init__(self)
		 
		 def query(self, text):
				result = []
				for song in songs:
					if text.lower() in song.findtext('title').lower() or text.lower() in song.findtext('artist').lower() or text.lower() in song.findtext('album').lower():	
						 self.title = song.findtext('title')
						 self.artist = song.findtext('artist')
						 self.album = song.findtext('album')
						 self.uri = song.findtext('location')
						 result.append(DeskRhythmMatch(self.title,self.uri, self.artist, self.album))
					
				if result.__len__() <= MAX_RESULTS and len(text) > 2 :
					self._emit_query_ready(text, result)



#############exaile


if USED_PLAYER=="exaile":
	
	try:
		from sqlite3 import dbapi2 as sqlite
	except ImportError:
		from pysqlite2 import dbapi2 as sqlite
	
	HANDLERS = ["ExaileCollectionSearch"]
	EXAILE_ICON_PATH = '/usr/share/app-install/icons/exaile.png'
	EXAILE_DB_PATH = os.path.expanduser('~/.exaile/music.db')
	EXAILE_DB_QUERY = \
	"""
	SELECT a.title, art.name AS artist, alb.name AS album, b.name AS path
	FROM tracks a, paths b, artists art, albums alb
	WHERE a.path = b.id
	AND a.artist = art.id
	AND a.album = alb.id
	"""
	class ExailePlayAction(deskbar.interfaces.Action):
		 def __init__(self, song):
				deskbar.interfaces.Action.__init__(self, song['path'])
				self._song = song

		 def activate(self, text=None):
				"""Plays this song.

				If Exaile is running, use dbus to tell it to play the song.
				If we can't find Exaile for dbus, start exaile on the command line.
				"""
				if not self.start_song():
					self._launch_exaile(self._absurl())

		 def start_song(self):
				"""Play this song in a running Exaile instance."""
				try:
					session = dbus.SessionBus()
					exaile = session.get_object('org.exaile.DBusInterface',
														 '/DBusInterfaceObject')
					if exaile:
						 exaile.play_file(self._absurl())
						 return Trueprint 
				except:
					pass
				return False

		 def _escape(self, url):
				return re.sub(r'(\W)', lambda x: '\\' + x.group(), url)
		 def _launch_exaile(self, url):
				os.system('exaile %s >/dev/null 2>&1 &' % self._escape(url))

		 def _absurl(self):
				return self._song['path']	 

		 def get_verb(self):
				"""Describes this search result for deskbar to display."""
				#return "Play <b>%s</b> in Exaile" % self._songname()
				out = 'Lyric of <b>'+self._songname()+'</b>\n by <i>'+self._song['artist']+'</i> from <i>'+self._song['album']+'</i>'				
				return out

		 def _songname(self):
				return " - ".join(
					[ self._song[x] for x in [ 'title', 'album', 'artist' ]
						if len(self._song[x]) > 0 ] )

		 def is_valid(self, text=None):
				return os.path.exists(self._song['path'])
		 
		 
	class ExailePlaylistMatch (deskbar.interfaces.Match):
		"""Deskbar Exaile search result."""
		def __init__(self, song, query):
			"""Initializes a deskbar match object, representing a search result."""
			deskbar.interfaces.Match.__init__(self)
			self._song = song
			self._query = query
			self._score = self._song_score()
			self.add_action( ExailePlayAction(self._song),True )
			self.add_action( DeskRhythmLyricAction(self._song['title'],self._song['artist'],self._song['album']))
			self.add_action( SearchLastFMAction(self._song['title'],self._song['artist'],self._song['album']))
			self.add_action( SearchLibreFMAction( self._song['title'], self._song['artist'],self._song['album']))
			self.add_action(SendToAction(self._song['title'], self._song['artist'], self._song['path']) )

		def __lt__(self, other):
			"""Compare match objects; more relevant matches go first when sorted."""
			return self._score > other._score or (self._score == other._score and self._song['title'] < other._song['title'])

		def _song_score(self):
			"""Returns a rough relevance number for a match, higher the better."""
			score = 0
			for key in self._song:
				if self._query.lower() in self._song[key].lower():
					score += 1
			return score

		def get_hash(self, text=None):
			"""Returns the song path for Deskbar to use as a hash key."""
			return self._song['path']

		
		
		
	
		
	class ExaileCollectionSearch(deskbar.interfaces.Module):
		INFOS = {	'icon':		deskbar.core.Utils.load_icon('audio-x-generic'),
						 'name':		'RhythmDesk',
						 'description':	'Search and change exaile playing song, get lyrics, search info',
						 'version':		'0.0.8'
		}		
		def __init__(self):
			deskbar.interfaces.Module.__init__(self)

		def initialize(self):
			"""Initialize Exaile search, loading collection catalog."""
			print "Initializing Exaile search"
			self.songs = [ ]
			self._load_catalog()

		def _load_catalog(self):
			try:
				dbconn = sqlite.connect(EXAILE_DB_PATH)
				if dbconn:
					 self._read_db_catalog(dbconn)
			except:
				print "Unable to read catalog from %s" % EXAILE_DB_PATH
				pass

		def _add_song(self, row):
			self.songs.append( { 'title'	: row[0],
										'artist' : row[1],
										'album'	: row[2],
										'path'	: row[3] } )
				
		def _read_db_catalog(self, conn):
			cursor = conn.cursor()
			try:
				cursor.execute(EXAILE_DB_QUERY)
				for row in cursor:
					 self._add_song([x or '' for x in row])
			finally:
				cursor.close()

		def _match(self, song, query):
			for key in song:
				if query.lower() in song[key].lower():
					 return True
			return False

		def query(self, query, max=MAX_RESULTS):
			"""Find up to max songs matching query, sorted by relevance."""
			if len(query) < 3:
				return []
			
			result = [ ExailePlaylistMatch(song, query)
						 for song in self.songs if self._match(song, query) ]
			result.sort()
			self._emit_query_ready( query, result )
			return result[:max]
	


	


