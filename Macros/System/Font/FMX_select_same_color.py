#FLM: FMX Select Same Color
# http://remix-tools.com/freemix
# (C) Tim Ahrens, 2012

from FL import *
try:
	dummy = set()
except:
	from sets import Set as set

colors = set ( [ glyph.mark for glyph in fl.font.glyphs if fl.Selected( glyph.index ) ] )

for glyph in fl.font.glyphs:
	if glyph.mark in colors:
		fl.Select( glyph.index )