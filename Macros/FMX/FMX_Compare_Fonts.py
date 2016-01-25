#FLM: FMX Compare Fonts

# some values that affect the formatting of the output
# adjust according to taste

# maximum number of kerning pairs to be mentioned explicitly
MAX_KERNING_PAIRS_EXPLICIT = 220

# maximum length of font info string to be displayed explicitly
MAX_LEN_FONT_INFO_EXPLICIT = 90

# maximum changes per category to be shown explicitly
MAX_CHANGES_PER_CATEGORY = 90

# justification of names (for alignment of descriptions)
JUST = 25

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##

from FL import *
import types
from FMX_glyph_table_copy import FLclasses
from FMX import sortinplace

FONT_INFO =	[
	'family_name', 'style_name', 'full_name', 'font_name', 'font_style', 'menu_name', 'apple_name', 'fond_id', 'pref_family_name', 'pref_style_name', 'mac_compatible', 'default_character', 'weight', 'weight_code', 'width', 'designer', 'designer_url', 'fontnames', 'copyright', 'notice', 'note', 'unique_id', 'tt_u_id', 'tt_version', 'trademark', 'x_u_id', 'vendor', 'vendor_url', 'version', 'year', 'version_major', 'version_minor', 'vp_id', 'ms_charset', 'ms_id', 'panose', 'pcl_chars_set', 'pcl_id',
	'upm', 'ascender', 'descender', 'cap_height', 'x_height', 'default_width', 'slant_angle', 'italic_angle', 'is_fixed_pitch', 'underline_position', 'underline_thickness',
	'blue_fuzz', 'blue_scale', 'blue_shift', 'blue_values', 'other_blues', 'family_blues', 'family_other_blues', 'force_bold', 'stem_snap_h', 'stem_snap_v'
	]


class ObjectWrapper( object ):
	def __init__(self, obj):
		self._obj = obj
	def __getattr__( self, name ):
		if hasattr( self._obj, name ):
			attr_value = getattr( self._obj,name )
			if isinstance( attr_value, types.MethodType ):
				def callable( *args, **kwargs ):
					return attr_value( *args, **kwargs )
				return callable
			else:
				return attr_value
		else:
			return getattr( self, name )
	# def __setattr__(self, name, value):
	# 	if (name == "_obj" or not hasattr(self, "_obj") or
	# 		not hasattr(self._obj, name) or name in dir(self)):
	# 		return super(ObjectWrapper, self).__setattr__(name, value)
	# 	else:
	# 		return setattr(self._obj, name, value)


class compGlyph( ObjectWrapper ):
	
	def __init__(self, obj):
		self._obj = obj
		# calculate median of x-values of all nodes (not BCPs) for each master
		if self.nodes:
			self.x_median = [ sortinplace( [ node.Layer(m)[0].x for node in self.nodes ] )[len(self.nodes)/2] for m in range( self.layers_number ) ]
		else:
			self.x_median = [ 0 ] * self.layers_number
	
	# returns the sidebearing, either LSB or RSB
	def metric( self, type, master ):
		if type == 'LSB':
			return self.GetBoundingRect(master).ll.x
		elif type == 'RSB':
			return self.GetMetrics(master).x - self.GetBoundingRect(master).ur.x
		elif type == 'width':
			return self.GetMetrics(master).x
	
	# returns a list of strings containing all point (node and BCP) coordinates, normalized to x-median = 0
	def outline_description( self, master ):
		return [ '%i %i' % ( p.x - self.x_median[master], p.y ) for node in self.nodes for p in node.Layer(master) ]
	
	# returns a list of strings with anchor coordinates, normalized to x-median = 0
	def anchors_description( self, master ):
		return sortinplace( [ '%i %i' % ( a.Layer( master ).y, a.Layer( master ).x - self.x_median[master] ) for a in self.anchors ] )
	
	# returns a list of anchor names
	def anchors_names( self ):
		return sortinplace( [ anchor.name for anchor in self.anchors ] )
	
	# returns a list of strings with component coordinates, normalized to x-median = 0
	def components_description( self, master ):
		return sortinplace( [ '%i %i' % ( c.deltas[master].y, c.deltas[master].x - self.x_median[master] ) for c in self.components ] )
	
	# returns a list of strings with hint direction/width/position, normalized to x-median = 0
	def hints_description( self, master ):
		hhints = [ 'h %i %i' % ( h.widths[master], h.positions[master] ) for h in self.hhints ]
		vhints = [ 'v %i %i' % ( h.widths[master], h.positions[master] - self.x_median[master] ) for h in self.vhints ]
		return sortinplace( hhints + vhints )
	
	# returns a list of strings with link direction/width/position, normalized to x-median = 0
	def links_description( self ):
		hlinks = [ 'h %i %i' % ( link.node1, link.node2 ) for link in self.hlinks ]
		vlinks = [ 'v %i %i' % ( link.node1, link.node2 ) for link in self.vlinks ]
		return sortinplace( hlinks + vlinks )
	
	# returns a string decribing changes to the outlines
	def outline_change( self, glyph ):
		# compare number of nodes
		if len( self.nodes ) > len( glyph.nodes ):
			if not glyph.nodes:
				return 'outline added'
			else:
				return 'nodes added'
		if len( self.nodes ) < len( glyph.nodes ):
			if not self.nodes:
				return 'outline removed'
			else:
				return 'nodes removed'
		# check each master for outline congruence
		changes = []
		for master in range( self.layers_number ):
			this_points = self.outline_description( master )
			othr_points = glyph.outline_description( master )
			if this_points != othr_points:
				this_points.sort()
				othr_points.sort()
				if this_points == othr_points:
					return 'starting point changed'
				changes.append( compFont( self.parent ).master_name( master ) + 'modified' )
				# TODO: details about the change (small tweak, redesign, shift up/down, overshoot etc.)
		return ', '.join( changes )
	
	# returns a string decribing changes to the metrics
	def spacing_change( self, glyph ):
		if not glyph or ( bool( self.nodes ) != bool( glyph.nodes ) ):
			return ''
		if self.nodes:
			metrics = [ 'LSB', 'RSB' ]
		else:
			metrics = [ 'width' ]
		changes = []
		for master in range( self.layers_number ):
			for metric in metrics:
				change = self.metric( metric, master ) - glyph.metric( metric, master )
				if change != 0:
					changes.append( ( '%s%s %s' % ( compFont( self.parent ).master_name( master ), metric, ( '+%i' % change ).replace( '+-', '-' ).rjust(3) ) ) )
		return ', '.join( changes )
	
	# returns a string decribing changes to the anchors
	def anchor_change( self, glyph ):
		# compare number of anchors
		if len( self.anchors ) > len( glyph.anchors ):
			return 'anchors added'
		if len( self.anchors ) < len( glyph.anchors ):
			return 'anchors removed'
		changes = []
		# compare anchor names
		if self.anchors_names() != glyph.anchors_names():
			changes.append( 'anchors renamed' )
		# compare anchor positions
		for master in range( self.layers_number ):
			if self.anchors_description( master ) != glyph.anchors_description( master ):
				changes.append( compFont( self.parent ).master_name( master ) + 'anchors moved' )
		return ', '.join( changes )
	
	# returns a string decribing changes to the components
	def component_change( self, glyph ):
		# compare number of components
		if len( self.components ) > len( glyph.components ):
			return 'components added'
		if len( self.components ) < len( glyph.components ):
			return 'components removed'
		changes = []
		# compare component positions
		for master in range( self.layers_number ):
			if self.components_description( master ) != glyph.components_description( master ):
				changes.append( compFont( self.parent ).master_name( master ) + 'components moved' )
		return ', '.join( changes )
	
	# returns a string decribing changes to the hints
	def hint_change( self, glyph ):
		changes = []
		for master in range( self.layers_number ):
			this_hints = self.hints_description( master )
			othr_hints = glyph.hints_description( master )
			# compare number of hints
			if len( this_hints ) > len( othr_hints ):
				return 'hints added'
			if len( this_hints ) < len( othr_hints ):
				return 'hints removed'
			# compare hint positions
			if this_hints != othr_hints:
				changes.append( compFont( self.parent ).master_name( master ) + 'hints changed' )
		return ', '.join( changes )
	
	# returns a string decribing changes to the links
	def link_change( self, glyph ):
		this_links = self.links_description()
		othr_links = glyph.links_description()
		# compare number of links
		if len( this_links ) > len( othr_links ):
			return 'links added'
		if len( this_links ) < len( othr_links ):
			return 'links removed'
		# compare link positions
		if len( self.nodes ) == len( glyph.nodes ) and this_links != othr_links:
			# TODO: better detect unchanged links
			# TODO: detect links converted to hints and vice versa
			return 'links modified'
		else:
			return ''
	
	# returns a string decribing changes to the note
	def note_change( self, glyph ):
		if self.note:
			if not glyph.note:
				return 'added "%s"' % self.note
			elif glyph.note != self.note:
				return 'changed "%s" to "%s"' % ( glyph.note, self.note )
		elif glyph.note:
				return 'removed "%s"' % glyph.note


class compFont( ObjectWrapper ):
	
	# returns whether any glyphs are selected (or false if it cannot be determined)
	def any_selected( self ):
		if self._obj.file_name == fl.font.file_name:
			# only one glyph selected counts as none selected
			if len( [ fl.Selected( glyph.index ) for glyph in self._obj.glyphs ] ) > 1:
				return True
		return False
	
	# returns whether the glyph counts as selected
	def is_selected( self, glyph ):
		if self.any_selected() and not fl.Selected( glyph.index ):
			return False
		else:
			return True
	
	# returns a list of selected glyphs, or all glyphs if none selected of font not active
	def selected_glyphs( self ):
		if self.file_name == fl.font.file_name:
			selection = [ glyph for glyph in self.glyphs if fl.Selected( glyph.index ) ]
			if len( selection ) >= 2:
				return selection
		return self.glyphs
	
	# generate a string such as 'Wt1 Wd0', based on the axis short names
	def master_name( self, master ):
		if self.axis:
			return '%s ' % ' '.join( [ '%s%i' % ( self.axis[a][1], ( master % 2**(a+1) ) / 2**a ) for a in range( len( this_font.axis ) ) ] )
		else:
			return ''
	
	# returns the same-named glyph or, if not present, one that matches the outline shape, or none
	def matching_glyph( self, glyph, search_shape = True ):
		# find glyph by name
		index = self._obj.FindGlyph( glyph.name )
		if index >= 0:
			return compGlyph( self._obj.glyphs[index] )
		# find glyph by unicode
		if glyph.unicode:
			index = self._obj.FindGlyph( glyph.unicode )
			if index >= 0:
				return compGlyph( self._obj.glyphs[index] )
		# find glyph by shape
		if search_shape:
			outline_description = sortinplace( compGlyph( glyph ).outline_description( 0 ) )
			for candidate in self.glyphs:
				# check nodes number
				if candidate.nodes_number == glyph.nodes_number:
					# make sure the candidate does not have a partner in the other font
					if not compFont( glyph.parent ).matching_glyph( candidate, search_shape = False ):
						continue
						# check whether the outlines match
						if sortinplace( compGlyph( candidate ).outline_description( 0 ) ) == outline_description:
							return compGlyph( candidate )
		return None
	
	# returns dict (pair as key) with all kerning pairs in the font
	def kerning_dict( self, allowed_names = [] ):
		if not allowed_names:
			allowed_names = [ glyph.name for glyph in self.selected_glyphs() ]
		kerning = {}
		for glyph in self.selected_glyphs():
			if glyph.name not in allowed_names:
				continue
			if glyph.unicode and glyph.unicode < 128:
				first_name = chr( glyph.unicode )
			else:
				first_name = glyph.name
			for k in glyph.kerning:
				second_glyph = self.glyphs[k.key]
				if second_glyph.name not in allowed_names:
					continue
				if second_glyph.unicode and second_glyph.unicode < 128:
					second_name = chr( second_glyph.unicode )
				else:
					second_name = second_glyph.name
				pair = '%s-%s' % ( first_name, second_name )
				if len( pair ) == 3:
					pair = pair.replace('-', '')
				kerning[ pair ] = [ int(v) for v in k.values ]
		return kerning
	
	# returns a list of strings that describe changes to the kerning
	def kerning_changes( self, font ):
		changes = []
		this_kerning = self.kerning_dict( allowed_names = [ glyph.name for glyph in font.glyphs ] )
		othr_kerning = font.kerning_dict( allowed_names = [ glyph.name for glyph in self.selected_glyphs() ] )
		# added_kerning
		added_kerning = [ k for k in this_kerning if not k in othr_kerning ]
		if len( added_kerning ) > MAX_KERNING_PAIRS_EXPLICIT:
			changes.append( 'added %i pairs' % len( added_kerning ) )
		elif added_kerning:
			changes.append( 'added %s' % ' '.join( added_kerning ) )
		# removed kerning
		removed_kerning = [ k for k in othr_kerning if not k in this_kerning ]
		if len( removed_kerning ) > MAX_KERNING_PAIRS_EXPLICIT:
			changes.append( 'removed %i pairs' % len( removed_kerning ) )
		elif removed_kerning:
			changes.append( 'removed %s' % ' '.join( removed_kerning ) )
		# changed kerning
		for master in range( self.glyphs[0].layers_number ):
			changed_kerning = [ k for k in this_kerning if k in othr_kerning and this_kerning[k][master] != othr_kerning[k][master] ]
			if len( changed_kerning ) > MAX_KERNING_PAIRS_EXPLICIT:
				changes.append( '%smodified %i pairs' % ( self.master_name( master ), len( changed_kerning ) ) )
			elif changed_kerning:
				changes.append( '%smodified %s' % ( self.master_name( master ), ' '.join( changed_kerning ) ) )
		return changes
	
	# returns a list of strings that describe changes to the font info
	def font_info_changes( self, font ):
		changes = []
		for info in FONT_INFO:
			try:
				this_info = str( getattr( self._obj, info ) )
				othr_info = str( getattr( font._obj, info ) )
				if this_info != othr_info:
					info = info.replace( '_', ' ' ).ljust(JUST)
					if len( this_info ) < MAX_LEN_FONT_INFO_EXPLICIT:
						changes.append( '%s changed to %s' % ( info, this_info ) )
					else:
						changes.append( '%s modified' % info )
			except AttributeError:
				pass
		return changes
	
	# returns list of glyphs that are not in the other font
	def added_glyphs( self, font ):
		added_glyphs_list = [ glyph.name for glyph in self.selected_glyphs() if not font.matching_glyph( glyph ) ]
		if len( added_glyphs_list ) > MAX_CHANGES_PER_CATEGORY:
			return [ '%i glyphs' % len( added_glyphs_list ) ]
		else:
			return added_glyphs_list
	
	# returns list of strings that describe renamings
	def glyph_name_changes( self, font ):
		changes = []
		for glyph in self.selected_glyphs():
			othr_glyph = font.matching_glyph( glyph )
			if othr_glyph and othr_glyph.name != glyph.name:
					changes.append( '%s renamed from %s' % ( glyph.name.ljust(JUST), othr_glyph.name ) )
		return changes
	
	# returns a list of tuples (category, list of change descriptions) of glyph level differences
	def glyph_level_changes( self, font ):
		categories = [ 'Unicode', 'Outlines', 'Components', 'Anchors', 'Hints', 'Links', 'Metrics', 'Notes' ]
		changes = dict( [ ( c, [] ) for c in categories ] )
		for glyph in self.selected_glyphs():
			change = {}
			this_glyph = compGlyph( glyph )
			othr_glyph = font.matching_glyph( glyph )
			# renaming
			if othr_glyph:
				change['Outlines'] = this_glyph.outline_change( othr_glyph )
				change['Components'] = this_glyph.component_change( othr_glyph )
				change['Anchors'] = this_glyph.anchor_change( othr_glyph )
				change['Hints'] = this_glyph.hint_change( othr_glyph )
				change['Links'] = this_glyph.link_change( othr_glyph )
				# TODO: TT-hinting
				# TODO: guides?
				change['Metrics'] = this_glyph.spacing_change( othr_glyph )
				change['Notes'] = this_glyph.note_change( othr_glyph )
				if glyph.unicode != othr_glyph.unicode:
					change['Unicode'] = 'unicode changed'
				# write non-empty entries to changes
				for category, entry in change.iteritems():
					if entry:
						changes[category].append( '%s %s' % ( glyph.name.ljust(JUST), entry ) )
		# return dict as list of tuples (in the desired order)
		for c in categories:
			if len( changes[c] ) > MAX_CHANGES_PER_CATEGORY:
				changes[c] = [ ( '%i glyphs' % len( changes[c] ) ).ljust(JUST) + ' modified' ]
		return [ ( c, changes[c] ) for c in categories if changes[c] ]
	
	# returns a list of strings that describe changes to classes
	def class_changes( self, font ):
		changes = []
		this_classes = FLclasses( self, split_classes = False )
		othr_classes = FLclasses( font, split_classes = False )
		# find added or modified classes
		for this_class in this_classes.glyph_classes:
			othr_class = othr_classes.matching_class( this_class )
			if othr_class:
				if this_class.name != othr_class.name:
					changes.append( '%s renamed from %s' % ( this_class.name.ljust(JUST), othr_class.name ) )
				else:
					if len( this_class.members ) > len( othr_class.members ):
						changes.append( '%s glyphs added' % this_class.name.ljust(JUST) )
					elif len( this_class.members ) < len( othr_class.members ):
						changes.append( '%s glyphs removed' % this_class.name.ljust(JUST) )
					elif not this_class.has_same_members( othr_class ):
						changes.append( '%s modified' % this_class.name.ljust(JUST) )
			else:
				changes.append( '%s added' % this_class.name.ljust(JUST) )
		# find removed classes
		for othr_class in othr_classes.glyph_classes:
			if not this_classes.matching_class( othr_class ):
				changes.append( '%s removed' % othr_class.name.ljust(JUST) )
		return changes
	
	# returns dict with all features in the font
	def features_dict( self ):
		return dict( [ ( feature.tag, feature.value ) for feature in self.features ] )
	
	# returns a list of strings that describe changes to classes
	def feature_changes( self, font ):
		changes = []
		this_features = self.features_dict()
		othr_features = font.features_dict()
		for tag, text in this_features.iteritems():
			if not tag in othr_features:
				changes.append( '%s added' % tag )
			elif text != othr_features[tag]:
				changes.append( '%s modified' % tag )
		for tag, text in othr_features.iteritems():
			if not tag in this_features:
				changes.append( '%s removed' % tag )
		return changes
	
	# returns a list of tuples (category, list of change descriptions) of all differences to the other font
	def what_has_changed( self, font ):
		all_changes = []
		# warning if axes were changed
		if self.axis != font.axis:
			all_changes.append( ( 'Multiple Master', [ 'Axes changed. Some comparisons are not performed.' ] ) )
		# removed, added and renamed glyphs
		glyph_changes = [ '%s removed' % glyphname.ljust(JUST) for glyphname in font.added_glyphs( self ) ]
		glyph_changes += [ '%s added' % glyphname.ljust(JUST) for glyphname in self.added_glyphs( font ) ]
		glyph_changes += self.glyph_name_changes( font )
		all_changes.append( ( 'Glyphs', glyph_changes ) )
		# glyph-level changes
		all_changes += self.glyph_level_changes( font )
		# other changes
		all_changes.append( ( 'Kerning', self.kerning_changes( font ) ) )
		all_changes.append( ( 'Font Info', self.font_info_changes( font ) ) )
		all_changes.append( ( 'Classes', self.class_changes( font ) ) )
		all_changes.append( ( 'Features', self.feature_changes( font ) ) )
		# return only non-empty categories
		return [ c for c in all_changes if c[1] ]
	


if len( fl ) != 2:
	fl.Message( 'The idea is to compare two revisions of a font.', 'This macro requires exactly two fonts to be opened in FontLab.' )
else:
	print '...'
	this_font = compFont( fl.font )
	othr_font = compFont( fl[1-fl.ifont] )
	whc = this_font.what_has_changed( othr_font )
	fl.output = ''
	if not whc:
		print 'No changes found.'
	for category, changes in whc:
		print
		print category
		upm_sensitive = [ 'Kerning', 'Outlines', 'Components', 'Anchors', 'Hints', 'Links', 'Metrics' ]
		if category in upm_sensitive and this_font.upm != othr_font.upm:
			print '    Not compared since fonts have different UPM.'
		else:
			for change in changes:
				print '    ' + change
	# TODO: mark modified glyphs
	# TODO: allow revert
