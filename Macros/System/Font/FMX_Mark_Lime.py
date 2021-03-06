#FLM: FMX Mark Lime
# http://remix-tools.com/freemix
# (C) Tim Ahrens, 2012

from FL import *
import FMX

def colour(font, glyph, gindex):
  glyph.mark = FMX.MARK_LIME
  fl.UpdateGlyph(gindex)

fl.ForSelected(colour)
fl.UpdateFont()
fl.font.modified = 1
