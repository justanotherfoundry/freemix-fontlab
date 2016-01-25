#FLM: FMX Metrics Class R
# http://remix-tools.com/freemix
# (C) Tim Ahrens, 2012

from FL import *

def add_class(ac_font, ac_glyph, ac_gindex):
  classes = ac_font.classes
  classes.append(".R_" + ac_glyph.name +": " + ac_glyph.name +"' ")
  ac_font.classes = classes

fl.ForSelected(add_class)
fl.UpdateFont()
fl.font.modified = 1
