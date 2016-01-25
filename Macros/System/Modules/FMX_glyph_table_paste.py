# This module is part of the Freemix Tools for FontLab.
# See remix-tools.com/freemix for info.
# (C) Tim Ahrens, 2012

from FL import *
import FMX_glyph_table_copy

class FMXdialog( FMX_glyph_table_copy.FMXdialog ):
	def __init__( self ):
		number_of_masters = fl.font[0].layers_number
		self.d = Dialog( self )
		self.d.title = 'FMX Glyph Table'
		# TODO: remember position
		self.d.Center ()
		x = 25
		y = 25
		line_height = 22
		dialog_height = 125
		if number_of_masters > 1:
			dialog_height += ( number_of_masters + 1 ) * line_height
		self.d.size = Point ( 330, dialog_height )
		# top text
		self.d.AddControl ( STATICCONTROL, Rect( x, y, 330, 60 ), 'top_text', STYLE_LABEL, 'Update font from clipboard?\nNote: This is not undoable.' )
		y += 28
		x += 12
		# radio buttons for master selection
		if number_of_masters > 1:
			for i in range( number_of_masters ):
				master_name = ''
				for a in range( len( fl.font.axis ) ):
					master_name += ' apply to %s%i' % ( fl.font.axis[a][1], (i/2**a) % 2 )
				y += line_height
				self.d.AddControl( CHECKBOXCONTROL, Rect( x, y, 300, aAUTO ), 'master%i' % i, self.STYLE_RADIO, master_name )
	def on_ok( self, code ):
		return 1


def paste_table( clip_columns, clip_rows, font, master = 0 ):
	fl.Unselect()
	# prepare classes
	fl_classes = FMX_glyph_table_copy.FLclasses( font )
	spacing_tool = FMX_glyph_table_copy.FMXspacingtool( font, master )
	# TODO: detect multiple treatment
	# treat each row
	for clip_row in clip_rows:
		row = dict( zip( clip_columns, [ item.strip() for item in clip_row.split( '\t' ) ] ) )
		# full name
		try:
			full_name = row['base name']
		except:
			print row
			continue
		if row.has_key( 'extension' ):
			full_name += row['extension'].replace( "'", "" ) # in case a ' was added in order to mask decimal fractions
		if not full_name:
			continue
		# find glyph by either index or name
		if row.has_key( 'index' ):
			if row['index']:
				try:
					glyph_index = int( row['index'] )
				except:
					continue
			else:
				if full_name:
					print 'Empty index. Adding glyphs not supported yet.'
				continue
			if glyph_index < 0 or glyph_index >= len( font.glyphs ):
				print 'Error: index out of bounds.'
				continue
		else:
			glyph_index = font.FindGlyph( full_name )
			if glyph_index < 0:
				print 'Error:', [full_name], 'not in font'
				continue
		glyph = font.glyphs[glyph_index]
		# select glyph
		# fl.Select( glyph_index )
		# name
		if not full_name:
			print 'Empty name. Deleting glyphs not supported yet.'
		elif glyph.name != full_name:
			print 'Glyph', glyph.name, 'renamed', full_name
			glyph.name = full_name
		# replace base name/comp
		for column in [ 'unicode', 'LSB', 'RSB', 'kern before', 'kern after' ]:
			if row.has_key( column ):
				# these often do not replace anything
				if row.has_key( 'base comp' ) and row['base comp']:
					row[column] = row[column].replace( '(base comp)', row['base comp'].split()[-1] )
				row[column] = row[column].replace( '(base name)', row['base name'] )
				row[column] = row[column].replace( '(base name LC)', row['base name'].lower() )
		# unicode
		if row.has_key( 'unicode' ):
			if row['unicode']:
				try:
					new_unicode = int( row['unicode'], 16 )
				except ValueError:
					glyph_index = font.FindGlyph( row['unicode'] )
					if glyph_index < 0:
						print 'Error while assigning Unicode to %s: %s not found.' % ( glyph.name, row['unicode'] )
						new_unicode = glyph.unicode
					else:
						new_unicode = font[glyph_index].unicode
				if glyph.unicode != new_unicode:
					print 'Unicode of', glyph.name, 'changed to', new_unicode
					glyph.unicode = new_unicode
			elif glyph.unicode:
				glyph.unicodes = []
				print 'Unicode removed from', glyph.name
		# possibly remove nodes
		if row.has_key( 'nodes' ) and not row['nodes'] and glyph.nodes:
			glyph.Clear()
			print 'Removed outline from', glyph
		# anchors
		if row.has_key( 'anchors' ):
			pasted_anchors = [ a for a in row['anchors'].split( ';' ) if a ]
			# delete superfluous anchors
			for i in range( len( pasted_anchors ), len( glyph.anchors ), 1 ):
				del glyph.anchors[ len( glyph.anchors ) - 1 ]
				print 'Anchor deleted from', glyph.name
			# add new anchors
			for i in range( len( glyph.anchors ), len( pasted_anchors ), 1 ):
				glyph.anchors.append( Anchor( 'anchor%i' % len( glyph.anchors ), 0, 0 ) )
				print 'Anchor added to', glyph.name
			# update all anchors
			for string, anchor in zip( pasted_anchors, glyph.anchors ):
				for item in string.replace( 'x ', 'x' ).replace( 'y ', 'y' ).split():
					try:
						x_or_y = item[0]
						value = int( item[1:] )
						if getattr( anchor, x_or_y ) != value:
							setattr( anchor.Layer( master ), x_or_y, value )
							print 'Anchor in', glyph.name, 'set', x_or_y
					except ValueError:
						if anchor.name != item:
							print 'Anchor', anchor.name, 'in', glyph.name, 'renamed', item
							anchor.name = item
		# components
		if row.has_key( 'base comp' ) and row['base comp']:
			pasted_comps = [ row['base comp'] ]
			if row.has_key( 'other comps' ):
				pasted_comps += [ a for a in row['other comps'].split( ';' ) if a ]
			# delete superfluous components
			for i in range( len( pasted_comps ), len( glyph.components ), 1 ):
				del glyph.components[ len( glyph.components ) - 1 ]
				print 'Component deleted from', glyph.name
			# add new components
			for i in range( len( glyph.components ), len( pasted_comps ), 1 ):
				glyph.components.append( Component( -1, Point( 0, 0 ) ) )
				print 'Component added to', glyph.name
			# update all components
			for string, component in zip( pasted_comps, glyph.components ):
				for item in string.replace( 'x ', 'x' ).replace( 'y ', 'y' ).split():
					try:
						x_or_y = item[0]
						value = int( item[1:] )
						if getattr( component.deltas[master], x_or_y ) != value:
							delta = component.deltas[master]
							setattr( delta, x_or_y, value )
							component.deltas[master] = delta
							print 'Component in', glyph.name, 'set to', x_or_y, '=', value
					except ValueError:
						index = font.FindGlyph( item )
						if index < 0:
							print 'Error while processing components:', item
						elif component.index != index:
								print 'Component in', glyph.name, 'set to:', item
								component.index = index
		# metrics
		for type in [ 'LSB', 'RSB', 'width' ]:
			if row.has_key( type ):
				# current value
				actual = spacing_tool.get_value( glyph, master, type )
				key_glyph = ''
				if row[type]:
					try:
						# apply numeric value
						new_SB = int( float( row[type] ) )
					except ValueError:
						# get value from key
						key_glyph = row[type].split()[0]
						new_SB = spacing_tool.get_value( key_glyph, master, type )
					if new_SB == '':
						print 'Error: could not make sense of', type, row[type].split()[0]
						key_glyph = ''
					else:
						old_SB = spacing_tool.set_value( glyph, master, type, new_SB )
						if old_SB != new_SB:
							print type, 'of', glyph.name, 'changed by', int( abs( new_SB - old_SB ) )
				# update classes
				if key_glyph:
					fl_classes.make_key( glyph.name, key_glyph, type )
				elif not fl_classes.is_key( glyph.name, type ):
					# no key glyph found: remove from all classes 
					if fl_classes.remove_member( glyph.name, type ):
						print 'Removed from', type, 'class:', glyph.name
		# kerning
		for type in [ 'kern before', 'kern after' ]:
			if row.has_key( type ):
				if row[type] and font.FindGlyph( row[type].split()[0] ) >= 0:
					fl_classes.make_key( glyph.name, row[type].split()[0], type )
					# TODO: ask whether to keep exceptions
				else:
					if not row[type]:
						spacing_tool.remove_kerning( glyph, type )
					if not fl_classes.is_key( glyph.name, type ):
						# no key glyph found: remove from all classes 
						if fl_classes.remove_member( glyph.name, type ):
							print 'Removed from', type, 'class:', glyph.name
		# OT classes
		if row.has_key( 'OT classes' ):
			# remove from all OT classes
			fl_classes.remove_member( glyph, 'OT' )
			# add as member
			if row['OT classes']:
				for class_name in row['OT classes'].split( ';' ):
					fl_classes.add_OT_member( glyph.name, class_name.strip() )
		# center
		if row.has_key( 'center' ) and row['center']:
			current_center = int( round( 0.5 * ( glyph.GetBoundingRect(master).ll.y + glyph.GetBoundingRect(master).ur.y ) ) )
			try:
				# apply numeric value
				shift_y = int( row['center'] ) - current_center
				notification = 'Shifted %s vertically by %i' % ( glyph.name, shift_y )
			except ValueError:
				# get value from name
				model_glyph = font[ row['center'].split()[0] ]
				model_center = int( round( 0.5 * ( model_glyph.GetBoundingRect(master).ll.y + model_glyph.GetBoundingRect(master).ur.y ) ) )
				shift_y = model_center - current_center
				notification = 'Shifted %s vertically to match %s' % ( glyph.name, row['center'] )
			# TODO: allow glyph name
			if shift_y != 0:
				glyph.Shift( Point( 0, shift_y ), master )
				print notification#.replace( 'vertically', { True:'up', False: 'down' }[ shift_y > 0 ] )
		# mark
		if row.has_key( 'mark' ):
			if row['mark']:
				mark = int( row['mark'] )
			else:
				mark = 0
			if glyph.mark != mark:
				# print 'Mark color of', glyph.name, 'changed to', mark
				glyph.mark = mark
		# selected
		if row.has_key( 'selected' ):
			fl.Select( glyph.index, row['selected'].strip() == True )
		# note
		if row.has_key( 'note' ):
			row['note'] = row['note'].strip()
			if glyph.note != row['note'] and ( glyph.note or row['note'] ):
				glyph.note = row['note']
				print 'Changed note on %s: %s' % ( glyph.name, glyph.note )
		fl.UpdateGlyph( glyph.index )
	fl_classes.write_to_FL()
	fl.UpdateFont()
	font.modified = 1
