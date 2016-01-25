# This module is part of the Freemix Tools for FontLab.
# See remix-tools.com/freemix for info.
# (C) Tim Ahrens, 2012

from FL import *
try:
	dummy = set()
except:
	from sets import Set as set
from feaTools_parser import parseFeatures
from FMX_glyph_table_feature_writer import FMXWriter

KERNING_INDICATOR = unichr( 0x25CF ) # 0x25CF BLACK CIRCLE
KERNING_EXCEPTION_INDICATOR = unichr( 0x25CB ) # 0x25CF WHITE CIRCLE
SIDEBEARING_MISMATCH_WARNING = unichr( 0x26A0 ) # 0x25CF WARNING SIGN
NBSP = unichr( 0x00A0 ) # non-breaking space
dialog_selection = []
dialog_selected_master = 0

class FMXdialog:
	column_groups = [
		( 'ALWAYS', [ 'index', 'base name', 'extension' ] ),
		( 'unicode', [ 'unicode', 'char' ] ),
		( 'elements', [ 'nodes', 'anchors', 'base comp', 'other comps' ] ),
		( 'metrics', [ 'LSB', 'RSB', 'width' ] ),
		( 'kerning', [ 'kern before', 'kern after' ] ),
		( 'stems', [ 'h-stems', 'v-stems' ] ),
		( 'alignment', [ 'top', 'center', 'bottom' ] ),
		( 'features', [ 'features' ] ),
		( 'other', [ 'OT classes', 'mark', 'selected', 'note' ] ) ]
	STYLE_RADIO = STYLE_CHECKBOX + cTO_CENTER
	def __init__( self, selection ):
		number_of_masters = fl.font[0].layers_number
		self.d = Dialog( self )
		self.d.title = 'FMX Glyph Table'
		# TODO: remember position
		self.d.Center ()
		x = 25
		y = 25
		line_height = 22
		dialog_height = 370
		if number_of_masters > 1:
			dialog_height += ( number_of_masters + 1 ) * line_height
		self.d.size = Point ( 330, dialog_height )
		# top text
		self.d.AddControl ( STATICCONTROL, Rect( x, y, 340, 100 ), 'top_text', STYLE_LABEL, 'This will copy glyph info to the clipboard\nfor pasting into a spreadsheet.' )
		y += 28
		x += 12
		# radio buttons for master selection
		if number_of_masters > 1:
			for i in range( number_of_masters ):
				master_name = ''
				for a in range( len( fl.font.axis ) ):
					master_name += ' %s%i' % ( fl.font.axis[a][1], (i/2**a) % 2 )
				y += line_height
				self.d.AddControl( CHECKBOXCONTROL, Rect( x, y, 300, aAUTO ), 'master%i' % i, self.STYLE_RADIO, master_name )
			y += line_height
		self.select_master( 0 )
		# load previous selection
		if 0 and not selection:
			selection = [ label for label, group in self.column_groups ]
		# show and set controls
		self.controls = [ label for label, group in self.column_groups if label != 'ALWAYS' ] + [ 'copy_empty_columns', 'add_help_row' ]
		for control in self.controls:
			y += line_height
			if control == 'copy_empty_columns':
				y += line_height * 0.5
			self.d.AddControl( CHECKBOXCONTROL, Rect( x, y, 300, aAUTO ), control, STYLE_CHECKBOX, ' ' + control.replace( '_', ' ' ) )
			setattr( self, control, 1 * ( control in selection ) )
	def select_master( self, master ):
		for i in range( 16 ):
			setattr( self, 'master%i' % i, 0 )
		setattr( self, 'master%i' % master, 1 )
		for i in range( 16 ):
			self.d.PutValue ( 'master%i' % i )
		self.selected_master = master
	def on_master0( self, code ): self.select_master( 0 )
	def on_master1( self, code ): self.select_master( 1 )
	def on_master2( self, code ): self.select_master( 2 )
	def on_master3( self, code ): self.select_master( 3 )
	def on_master4( self, code ): self.select_master( 4 )
	def on_master5( self, code ): self.select_master( 5 )
	def on_master6( self, code ): self.select_master( 6 )
	def on_master7( self, code ): self.select_master( 7 )
	def on_master8( self, code ): self.select_master( 8 )
	def on_master9( self, code ): self.select_master( 9 )
	def on_master10( self, code ): self.select_master( 10 )
	def on_master11( self, code ): self.select_master( 11 )
	def on_master12( self, code ): self.select_master( 12 )
	def on_master13( self, code ): self.select_master( 13 )
	def on_master14( self, code ): self.select_master( 14 )
	def on_master15( self, code ): self.select_master( 15 )
	def on_ok( self, code ):
		# update dialog
		for control in self.controls + [ 'master%i' % i for i in range( 16 ) ]:
			self.d.GetValue( control )
			self.d.Show( control, 0 )
		self.top_text = 'Copying...'
		self.d.PutValue( 'top_text' )
		# determine columns and store selection
		self.selection = [ control for control in self.controls if getattr( self, control ) ]
		columns = [ column for label, group in self.column_groups for column in group if label == 'ALWAYS' or label in self.selection ]
		# copy to clipboard
		if columns:
			self.string = copy_table( fl.font, self.selected_master, columns, self.copy_empty_columns, self.add_help_row )


class FMXclass:
	def __init__( self, type, string = '' ):
		self.type = type
		self.string = string
		self.members = []
		if string:
			self.members = string.split()
			self.name = self.members.pop( 0 )[:-1]
			# make key glyph the first and remove '
			for i in range( len( self.members ) ):
				member = self.members[i]
				if member.endswith( "'" ):
					del self.members[ i ]
					self.members.insert( 0, member[:-1] )
	def update_string( self ):
		# updates the string
		# metrics/kerning clases without followers are not stringified
		if self.type == 'OT':
			if self.members:
				self.string = self.name + ': ' + ' '.join( self.members )
			else:
				self.string = ''
		else:
			if len( self.members ) >= 2:
				self.string = self.name + ': ' + self.members[0] + "' " + ' '.join( self.members[1:] )
			else:
				self.string = ''
	def remove_member( self, glyph_name ):
		try:
			self.members.remove( glyph_name )
			self.update_string()
			return True
		except ValueError:
			return False
	def add_member( self, glyph_name ):
		if glyph_name in self.members:
			return False
		else:
			self.members.append( glyph_name )
			self.update_string()
			return True
	def merge_flags( self, other_class ):
		# don't merge auto-created SB classes (see FL bug):
		if not self.name.endswith( 'SB' ) and not other_class.name.endswith( 'SB' ):
			# check whether types are compatible (i.e. both SB or both kern)
			if self.name[0] == other_class.name[0]:
				# check for same key glyph
				if self.members[0] == other_class.members[0]:
					# check for same members
					if set( self.members ) == set( other_class.members ):
						return [ a + b for a, b in zip( self.flags(), other_class.flags() ) ]
		return []
	def flags( self ):
		flags_map = { 'kern before': [ 0, 1 ], 'kern after': [ 1, 0 ], 'LSB': [ 1, 0, 0 ], 'RSB': [ 0, 1, 0 ], 'width': [ 0, 0, 1 ], 'OT': [ 0, 0 ] }
		return flags_map[self.type]


class FLclasses:
	def __init__( self, font ):
		self.font = font
		# build classes
		self.glyph_classes = []
		for i in range( len( font.classes ) ):
			string = font.classes[i]
			if string.startswith( '_' ):
				if font.GetClassRight( i ):
					self.glyph_classes.append( FMXclass( 'kern before', string ) )
			 	if font.GetClassLeft( i ):
					self.glyph_classes.append( FMXclass( 'kern after', string ) )
			elif string.startswith( '.' ):
				if font.GetClassMetricsFlags( i )[0]:
					self.glyph_classes.append( FMXclass( 'LSB', string ) )
				if font.GetClassMetricsFlags( i )[1]:
					self.glyph_classes.append( FMXclass( 'RSB', string ) )
				if font.GetClassMetricsFlags( i )[2]:
					self.glyph_classes.append( FMXclass( 'width', string ) )
				# if unflagged (probably due to FL bug): look for LSB/RSB in name
				if not 1 in font.GetClassMetricsFlags( i ) and len( string ) >= 4 and string[1:5] in [ 'RSB_', 'LSB_' ]:
					self.glyph_classes.append( FMXclass( string[1:4], string ) )
			else:
				self.glyph_classes.append( FMXclass( 'OT', string ) )
	def is_key( self, glyph_name, type ):
		for glyph_class in self.glyph_classes:
			if glyph_class.type == type and glyph_name == glyph_class.members[0]:
				return glyph_class
		return False
	def find_key( self, glyph_name, type ):
		# return FMXclass where glyph_name is the key, or ''
		for glyph_class in self.glyph_classes:
			if glyph_class.type == type and glyph_name in glyph_class.members:
				return glyph_class.members[0]
		return ''
	def find_classnames( self, glyph_name, type ):
		return [ glyph_class.name for glyph_class in self.glyph_classes if glyph_class.type == type and glyph_name in glyph_class.members ]
	def remove_member( self, glyph_name, type ):
		return True in [ glyph_class.remove_member( glyph_name ) for glyph_class in self.glyph_classes if glyph_class.type == type ]
	def add_OT_member( self, glyph_name, OT_class_name ):
		existing = [ c for c in self.glyph_classes if c.name == OT_class_name ]
		if existing:
			# add as member to existing class
			if existing[0].add_member( glyph_name ):
				print 'Added', glyph_name, 'to OT class', OT_class_name
		else:
			# create new class
			new_class = FMXclass( 'OT' )
			new_class.name = OT_class_name
			new_class.add_member( glyph_name )
			self.glyph_classes.append( new_class )
	def make_key( self, glyph_name, key, type ):
		if glyph_name != key:
			matching_class = self.is_key( key, type )
			if not matching_class:
				# remove key and glyph from existing classes
				self.remove_member( glyph_name, type )
				self.remove_member( key, type )
				# generate new class
				new_class = FMXclass( type )
				type_indicator = { 'kern before': '_', 'kern after': '_', 'LSB': '.LSB_',  'RSB': '.RSB_',  'OT': ''  }
				# TODO: remove _LSB if it becomes an RSM class as well
				new_class.name = type_indicator[type] + key
				existing_classnames = [ glyph_class.name for glyph_class in self.glyph_classes ]
				while new_class.name in  existing_classnames:
					new_class.name += '_'
				new_class.add_member( key )
				new_class.add_member( glyph_name )
				self.glyph_classes.append( new_class )
				print 'Created new class:', key + "'", glyph_name, '-', type
			elif glyph_name not in matching_class.members:
				# add to matching class
				self.remove_member( glyph_name, type )
				matching_class.add_member( glyph_name )
				print 'Added', glyph_name, 'to', key, '-', type
	def write_to_FL( self ):
		# writes the classes to FL
		font_classes = []
		all_flags = []
		for glyph_class in self.glyph_classes:
			if glyph_class.string:
				# search for compatible class to merge with
				for other_class in self.glyph_classes:
					merged_flags = glyph_class.merge_flags( other_class )
					if merged_flags:
						try:
							# found a matching class but it might be glyph_class itself or after glyph_class
							i = font_classes.index( other_class.string )
							all_flags[i] = merged_flags
							break
						except ValueError:
							pass
				else:
					all_flags.append( glyph_class.flags() )
					font_classes.append( glyph_class.string )
		# write clases
		self.font.classes = font_classes
		# set flags
		for i in range( len( all_flags ) ):
			flags = all_flags[i]
			current_flags = self.font.GetClassMetricsFlags( i )
			# change only if it is not already as should be
			if current_flags != tuple( flags ):
				try:
					# metrics classes
					self.font.SetClassFlags( i, flags[0], flags[1], flags[2] )
					if self.font.GetClassMetricsFlags(i) != tuple( flags ):
						print 'Note: Due to a bug in the FontLab API, the flags of a RSB class could not be set. Please correct manually.'
						self.font.SetClassFlags( i, flags[0], 0, 0 )
				except IndexError:
					# kerning classes (also catches OT classes)
					self.font.SetClassFlags( i, flags[0], flags[1] )


class FMXspacingtool:
	def __init__( self, font, master ):
		# all right glyphs (for kerning before)
		self.kerning_right_glyphs = set( [ pair.key for glyph in font.glyphs for pair in glyph.kerning if pair.values[master] != 0 ] )
		self.font = font
	def get_glyph( self, glyph ):
		if not type( glyph ) is str:
			return glyph
		index = self.font.FindGlyph( glyph )
		if index >= 0:
			return self.font[index]
		return None
	def get_value( self, glyph, master, metric ):
		glyph = self.get_glyph( glyph )
		if glyph == None:
			print 'get_value error', metric
			return ''
		# kerning
		if metric == 'kern after':
			right_hand_kerning = [ k.values[master] for k in glyph.kerning if k.values[master] ]
			if right_hand_kerning:
				return True
			return False
		if metric == 'kern before':
			return glyph.index in self.kerning_right_glyphs
		# width
		if metric == 'width':
			return glyph.GetMetrics( master ).x
		# sidebearing
		if metric == 'LSB':
			value = int( glyph.GetBoundingRect(master).ll.x )
		if metric == 'RSB':
			value = int( glyph.GetMetrics( master ).x - glyph.GetBoundingRect(master).ur.x )
		if value < 32000:
			return value
		return ''
	def set_value( self, glyph, master, metric, new_value ):
		glyph = self.get_glyph( glyph )
		old_value = self.get_value( glyph, master, metric )
		if glyph == None or old_value == '' or old_value == new_value:
			return old_value
		# shift glyph
		if metric == 'LSB':
			glyph.Shift( Point( new_value - old_value, 0 ), master )
		# adjust advance width
		if metric in [ 'LSB', 'RSB', 'width' ]:
			metrics = glyph.GetMetrics( master )
			metrics.x += new_value - old_value
			glyph.SetMetrics( metrics, master )
		return old_value
	def remove_kerning( self, glyph, metric ):
		if metric == 'kern after':
			if glyph.kerning:
				glyph.kerning = []
				print 'Kerning after', glyph.name, 'removed.'
		elif metric == 'kern before' and glyph.index in self.kerning_right_glyphs:
			self.kerning_right_glyphs.remove( glyph.index )
			print 'Kerning before', glyph.name, 'removed.'
			for left_glyph in self.font.glyphs:
				for k in range( len( left_glyph.kerning ) ):
					if left_glyph.kerning[k].key == glyph.index:
						del left_glyph.kerning[k]
						break


def copy_table( font, master, columns, copy_empty_columns, add_help_row ):
	fl_classes = FLclasses( font )
	spacing_tool = FMXspacingtool( font, master )
	# any glyphs selected?
	any_selected = 1 in [ fl.Selected( i ) for i in range( len( font ) ) ]
	help_row = {
			'index': u'FontLab\u2019s internal index. Not editable. If this column is not pasted then the name will be the glyph identifier.',
			'base name': 'Glyph name excluding extension. This column must always be pasted. Editable if index column is pasted.',
			'extension': 'Glyph name extension. Editable if index column is pasted.',
			'unicode': 'Unicode value. Multiple values per glyph not supported. Editable. Can be removed by erasing the cell.',
			'char': 'Glyph as character, based on unicode. Not editable.',
			'nodes': 'Number of nodes. Outline can be removed by erasing the cell.',
			'anchors': 'Position and name of anchors. Editable. It is possible to specify only x, y or the name.',
			'base comp': 'Position and name of first component. Editable. It is possible to specify only x, y or the name.',
			'other comps': 'Position and name of other components. Editable. It is possible to specify only x, y or the name.',
			'LSB': 'Left sidebearing. Glyph name indicates key of class. Editable, can be used to add or modify metrics classes.',
			'RSB': 'Right sidebearing. Glyph name indicates key of class. Editable, can be used to add or modify metrics classes.',
			'width': 'Advance width. Glyph name indicates key of class. Not editable yet.',
			'kern before': 'Kerning to the left of the glyph. Glyph name indicates key of class. White dots indicate exceptions. Black dots represent existing kerning. Editable, can be used to add or modify kerning classes. Kerning can be removed by erasing the cell.',
			'kern after': 'Same as before but kerning to the right of the glyph.',
			'h-stems': 'Horizontal stems, based on hints. Not editable.',
			'v-stems': 'Vertical stems, based on hints. Not editable.',
			'top': 'Top of the bounding box. Not editable.',
			'center': 'Height of the center of the glyph. Editable. Try entering a glyph name, this can be useful for vertically centering case-sensitive punctuation.',
			'bottom': 'Bottom of the bounding box. Not editable.',
			'OT classes': 'OpenType classes that contain the glyph. Editable, can be used to add or modify OpenType classes.',
			'mark': 'Color of the glyph as a number between 0 and 255. Editable.',
			'selected': 'Indicates whether the glyph is selected. Editable, anything non-empty will make the glyph selected.',
			'note': 'Glyph note. Editable.'
		}
	# find all substituions in OT features
	all_subs = {}
	if 'features' in columns:
		columns.remove( 'features' )
		for feature in fl.font.features:
			if feature.tag != 'kern':
				column = feature.tag + ' sub'
				columns.append( column )
				writer = FMXWriter( isFeature = True )
				parseFeatures( writer, fl.font.classes_text + feature.value )
				for subsitute, source in writer.subs:
					if not all_subs.has_key( subsitute ):
						all_subs[subsitute] = []
					all_subs[subsitute].append( ( column, source ) )
				help_row[column] = 'Glyph(s) substituted in feature %s. Not editable yet.' % feature.tag
	if add_help_row:
		rows = [ help_row, {} ]
	else:
		rows = [ {} ]
	# dump data for each glyph
	for glyph in font.glyphs:
		if any_selected and not fl.Selected( glyph.index ):
			continue
		row = {}
		row['index'] = glyph.index
		row['bottom'] = int( glyph.GetBoundingRect(master).ll.y )
		row['top'] = int( glyph.GetBoundingRect(master).ur.y )
		row['center'] = int( round( 0.5 * ( row['bottom'] + row['top'] ) ) )
		# TODO: show in relation to alignment zones
		# TODO: show center relative to cap/2
		row['note'] = unicode( glyph.note ).replace( 'None', '' )
		row['mark'] = ( '_' + str( glyph.mark ) ).replace( '_0', '' ).replace( '_', '' )
		row['selected'] = ( str( fl.Selected( glyph.index ) ).replace( '1', KERNING_INDICATOR ).replace( '0', '' ) )
		# glyph name and extension
		split_name = glyph.name.strip( '.' ).split( '.' )
		if len( split_name ) == 1:
			row['extension'] = ''
			row['base name'] = glyph.name
		else:
			row['base name'] = '.'.join( split_name[:-1] )
			row['extension'] = glyph.name[len( row['base name'] ):]
		# prevent extension from being interpreted as a decimal fraction
		if row['extension'] and row['extension'][1] in '0123456789':
			row['extension'] = "'" + row['extension']
		# the glph itself as a char (if possible)
		if glyph.unicode:
			row['char'] = unichr( glyph.unicode ).replace( '\'', '\'\'').replace( '"', '\'"')
			row['unicode'] = ( "0x%0.4X" % glyph.unicode )
		# TODO: links
		for key, hints in [ ( 'h-stems', glyph.hhints ), ( 'v-stems', glyph.vhints ) ]:
			# collect hints, filter out ghost hints
			row[key] = [ hint.widths[master] for hint in hints if hint.width > 0 ]
			if row[key]:
				row[key].sort()
				row[key].reverse()
				row[key] = repr( row[key] ).replace( '[', '' ).replace( ']', '' )
			else:
				row[key] = ''
		# anchors
		row['anchors'] = '; '.join( [ 'y%i x%i %s' % ( anchor.Layer( master ).y, anchor.Layer( master ).x, anchor.name ) for anchor in glyph.anchors ] )
		# OT classes
		row['OT classes'] = '; '.join( fl_classes.find_classnames( glyph.name, 'OT' ) )
		# kerning
		for metric in [ 'kern before', 'kern after' ]:
			if metric in columns:
				if fl_classes.is_key( glyph.name, metric ):
					# glyph is key
					row[metric] = glyph.name + ' ' + KERNING_INDICATOR
				else:
					row[metric] = fl_classes.find_key( glyph.name, metric )
					if spacing_tool.get_value( glyph, master, metric ):
						# glyph has kerning
						if row[metric] != '':
							# glyph has exceptions
							row[metric] += ' ' + KERNING_EXCEPTION_INDICATOR
						else:
							# glyph is solitair with kerning
							row[metric] = KERNING_INDICATOR
		# metrics
		for metric in [ 'LSB', 'RSB', 'width' ]:
			if metric in columns:
				actual = spacing_tool.get_value( glyph, master, metric )
				row[metric] = str( actual )
				if not fl_classes.is_key( glyph.name, metric ):
					key = fl_classes.find_key( glyph.name, metric )
					if key:
						row[metric] = key
						if actual != spacing_tool.get_value( key, master, metric ):
							row[metric] += ' ' + SIDEBEARING_MISMATCH_WARNING
		# number of nodes
		row['nodes'] = glyph.nodes_number
		if row['nodes'] == 0: row['nodes'] = ''
		# components
		all_comps = [ 'y%i x%i %s' % ( c.deltas[master].y, c.deltas[master].x, font[c.index].name ) for c in glyph.components ]
		if all_comps:
			row['base comp'] = all_comps.pop( 0 )
			row['other comps'] = '; '.join( all_comps )
		# fix completely empty glyphs
		if not glyph.components and not row['nodes']:
				for key in [ 'nodes', 'bottom', 'top', 'center', 'RSB', 'LSB' ]:
					row[key] = ''
		# OT substitutions
		if all_subs.has_key( glyph.name ):
			for column, source in all_subs[glyph.name]:
				row[column] = source
		# create meta glyph names
		# TODO: follow-ups like LSB of ccedilla is not O but (base comp)
		meta_names = []
		if row['extension']:
			meta_names.append( ( row['base name'], '(base name)' ) )
		if row.has_key( 'base comp' ) and row['base comp']:
			meta_names.append( ( row['base comp'].split()[-1], '(base comp)' ) )
		if row['base name'][0].isupper():
			meta_names.append( ( row['base name'].lower(), '(base name LC)' ) )
		potential_columns = [ 'LSB', 'RSB', 'kern before', 'kern after' ] + [ c for c in columns if c.endswith( ' sub' ) ]
		for column in potential_columns:
			if row.has_key( column ):
				for plain, meta in meta_names:
					padded_entry = ( ' %s ' % row[column] ).replace( '[', '[ ' ).replace( ']', ' ]' )
					padded_plain = ' %s ' % plain
					padded_meta = ' %s ' % meta
					row[column] = padded_entry.replace( padded_plain, padded_meta ).strip().replace( '[ ', '[' ).replace( ' ]', ']' )
		# turn everything into strings
		for key in row.keys():
			if type( row[key] ) is int:
				row[key] = str( row[key] ).strip()
		rows.append( row )
	# remove columns that would be empty
	if not copy_empty_columns:
		for column in columns[:]:
			if not True in [ row.has_key( column ) and row[ column ] != '' for row in rows ]:
				columns.remove( column )
	# prepare list with everything for the clipboard
	for_clipboard = [ '\t'.join( columns ), '\n' ]
	for row in rows:
		for column in columns:
			try:
				for_clipboard.append( row[ column ].replace( '\n', ' ' ).replace( '\r', ' ' ).replace( '\t', ' ' ).replace( '  ', ' ' ) )
			except KeyError:
				pass
			for_clipboard.append( '\t' )
		for_clipboard.pop() # remove last tab
		for_clipboard.append( '\n' )
	# return string for clipboard
	return ''.join( for_clipboard )


