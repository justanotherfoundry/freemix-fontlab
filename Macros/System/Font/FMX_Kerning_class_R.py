#FLM: FMX Kerning Class R
# http://remix-tools.com/freemix
# (C) Tim Ahrens, 2012

from FL import *

def add_class(ac_font, ac_glyph, ac_gindex):
  classes = ac_font.classes
  classes.append( "_" + ac_glyph.name + "_R: " + ac_glyph.name + "' " )
  ac_font.classes = classes
  ac_font.SetClassFlags(len(classes)-1, 0, 1)

fl.ForSelected(add_class)
fl.UpdateFont()
fl.font.modified = 1
