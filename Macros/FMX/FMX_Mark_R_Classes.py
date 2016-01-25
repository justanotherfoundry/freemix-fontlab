#FLM: FMX Mark R Classes
# http://remix-tools.com/freemix
# (C) Tim Ahrens, 2012

class_start = '_' # '.' for metrics classes, '_' for kerning classes

from FL import *
import FMX

f = fl.font

for i in range(len(f)): f[i].mark = 0

for c in range(len(f.classes)):
	class_elements = f.classes[c].split()
	class_name = class_elements.pop(0)
	if class_name.startswith( class_start ):
		for member in class_elements:
			if f.GetClassRight(c) or f.GetClassMetricsFlags(c)[1] or f.GetClassMetricsFlags(c)[2]:
				indx = f.FindGlyph(member.replace("'", ""))
				if indx == -1:
					print member, 'missing in', class_name
					continue
				glyph = f[indx]
				if glyph.mark == FMX.MARK_PROBLEM: continue
				# key
				if member[-1:] == "'":
					if glyph.mark == FMX.MARK_MEMBER:
						glyph.mark = FMX.MARK_KEY
					elif glyph.mark == FMX.MARK_KEY and not f.GetClassMetricsFlags(c)[2]:
						print glyph.name, "is a key glyph in several classes. It is recommended to unite these classes."
						glyph.mark = FMX.MARK_PROBLEM
					else:
						glyph.mark = FMX.MARK_KEY
				# non-key member
				else:
					if glyph.mark == FMX.MARK_MEMBER:
						print glyph.name, "is a non-key member several times. It is recommended to remove all but one."
						glyph.mark = FMX.MARK_PROBLEM
					elif glyph.mark == FMX.MARK_PROBLEM:
						pass
					else:
						glyph.mark = FMX.MARK_MEMBER

fl.UpdateFont()
