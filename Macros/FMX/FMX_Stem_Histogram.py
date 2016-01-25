#FLM: FMX Stem Histogram
# http://remix-tools.com/freemix
# (C) Tim Ahrens, 2012

from FL import *

if fl.Message( 'FMX Stem Histogram', 'Which stems to output?', 'Vertical', 'Horizontal' ) == 1:
	hv = 'v'
	xy = 'x'
else:
	hv = 'h'
	xy = 'y'

fl.output = ''
print hv, 'stems:\n'

for master in range( fl.font[0].layers_number ):
	frequencies = {}
	names = {}
	if fl.font[0].layers_number > 1:
		print '\n\n\nmaster', master
	for glyph in fl.font.glyphs:
		if fl.Selected( glyph.index ) or fl.count_selected < 5:
			hints = getattr( glyph, hv + 'hints' )
			for hint in hints:
				width = hint.widths[master]
				if hv == 'v' or width > 0:
					width = abs( width )
					# determine name string
					if glyph.unicode and glyph.unicode < 128:
						name = chr( glyph.unicode )
					else:
						name = glyph.name
					# add to names
					try:
						frequencies[width] += 1
						names[width] += ' ' + name
					except KeyError:
						frequencies[width] = 1
						names[width] = name
			links = getattr( glyph, hv + 'links' )
			for link in links:
				if link.node1 >= 0 and link.node2 >= 0:
					v1 = getattr( glyph.nodes[link.node1].Layer(master)[0], xy[hv] )
					v2 = getattr( glyph.nodes[link.node2].Layer(master)[0], xy[hv] )
					width = abs( v1 - v2 )
					# determine name string
					if glyph.unicode and glyph.unicode < 128:
						name = chr( glyph.unicode )
					else:
						name = glyph.name
					# add to names
					try:
						frequencies[width] += 1
						names[width] += ' ' + name
					except KeyError:
						frequencies[width] = 1
						names[width] = name
	
	if frequencies:
		for width in range( min( frequencies ), max( frequencies ) + 1 ):
			print str( width ).rjust( 2 ),
			try:
				print ''.join( [ '*' * frequencies[width] ] )
			except KeyError:
				print
		print
		for width in range( min( frequencies ), max( frequencies ) + 1 ):
			print str( width ).rjust( 2 ),
			try:
				print '   ' + ''.join( names[width] )
			except KeyError:
				print
	else:
		print 'This tool needs hints or links.\nWhy not quickly autohint the font and try again?'
