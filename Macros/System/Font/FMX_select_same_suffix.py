#FLM: FMX Select Same Suffix
# http://remix-tools.com/freemix
# (C) Tim Ahrens, 2012

from FL import *
try:
	dummy = set()
except:
	from sets import Set as set

suffixes = set ()
for glyph in fl.font.glyphs:
	if fl.Selected(glyph.index):
		try:
			suffixes.add( '.' + glyph.name.split('.', 1)[1] )
		except:
			pass

for glyph in fl.font.glyphs:
	if True in [ glyph.name.endswith(s) for s in suffixes ]:
		fl.Select( glyph.index )