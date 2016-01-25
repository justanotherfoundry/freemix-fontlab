# This module is part of the Freemix Tools for FontLab.
# See remix-tools.com/freemix for info.
# (C) Tim Ahrens, 2012

from feaTools_fdkSyntaxWriter import FDKSyntaxFeatureWriter

class FMXWriter( FDKSyntaxFeatureWriter ):
	subs = []
	def __init__( self, name = None, isFeature = False ):
		self.class_definitions = {}
		if isFeature:
			self.subs = []
		super( FMXWriter, self ).__init__( name = name, isFeature = isFeature )
	def _make_plain_list( self, stuff ):
		plain_list = []
		if isinstance( stuff, list ):
			for item in stuff:
				plain_list.extend( self._make_plain_list( item ) )
		elif stuff.startswith( '@' ) and self.class_definitions.has_key( stuff ):
			plain_list = self._make_plain_list( self.class_definitions[stuff] )
		else:
			plain_list = [ stuff ]
		return plain_list
	def classDefinition( self, name, contents ):
		# print 'classDefinition'
		self.class_definitions[name] = contents
	def _subwriter( self, name, isFeature ):
		return self
		return FMXWriter( name, isFeature = isFeature )
	def gsubType1( self, target, replacement ):
		# simple substitution
		for subsitute, source in zip( self._make_plain_list( replacement ), self._make_plain_list( target ) ):
			# print subsitute, source
			self.subs.append( ( subsitute, source ) )
	def gsubType4( self, target, replacement ):
		# target is always a list
		self.subs.append( ( replacement, self._list2String( target ) ) )
	def gsubType6( self, precedingContext, target, trailingContext, replacement ):
		if isinstance( precedingContext, list ):
			precedingContext = self._list2String( precedingContext )
		if isinstance( target, list ):
			finalTarget = []
			for t in target:
				if isinstance( t, list ):
					t = "[%s]" % self._list2String( t )
				finalTarget.append( t + "'" )
			target = " ".join( finalTarget )
		else:
			target += "'"
		if isinstance( trailingContext, list ):
			trailingContext = self._list2String( trailingContext )
		if isinstance( replacement, list ):
			replacement = self._list2String( replacement )
		# if the replacement is None, this is an "ignore"
		if replacement is None:
			print 'FMX gsubType6: ignore not supported yet.'
			if precedingContext and trailingContext:
				t = "ignore sub %s %s %s;" % ( precedingContext, target, trailingContext )
			elif precedingContext:
				t = "ignore sub %s %s;" % ( precedingContext, target )
			elif trailingContext:
				t = "ignore sub %s %s;" % ( target, trailingContext )
			else:
				t = "ignore sub %s;" % target
		# otherwise it is a regular substitution
		else:
			# FMX
			source = ( '%s %s %s' % ( precedingContext, target, trailingContext ) ).strip()
			self.subs.append( ( replacement, source ) )
			# print 'FMX gsubType6 in', self._name
