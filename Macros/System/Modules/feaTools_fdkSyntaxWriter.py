"""
Basic FDK syntax feature writer.
"""


from feaTools_baseWriter import AbstractFeatureWriter


class FDKSyntaxFeatureWriter(AbstractFeatureWriter):

	def __init__(self, name=None, isFeature=False):
		self._name = name
		self._isFeature = isFeature
		self._indentationLevel = 0
		self._instructions = []

	def write(self, linesep="\n"):
		lines = []
		if self._name:
			lines.append("")
			if self._isFeature:
				t = self._whitespace(self._indentationLevel-1) + "feature %s {" % self._name
				lines.append(t)
			else:
				t = self._whitespace(self._indentationLevel-1) + "lookup %s {" % self._name
				lines.append(t)
		for instrution in self._instructions:
			if isinstance(instrution, FDKSyntaxFeatureWriter):
				t = instrution.write(linesep)
				lines.append(t)
			else:
			   t = self._whitespace() + instrution
			   lines.append(t)
		if self._name:
			t = self._whitespace(self._indentationLevel-1) + "} %s;" % self._name
			lines.append(t)
			lines.append("")
		return linesep.join(lines)

	def _whitespace(self, level=None):
		if level is None:
			level = self._indentationLevel
		return "   " * level

	def _list2String(self, aList):
		final = []
		for i in aList:
			if isinstance(i, list):
				i = "[%s]" % self._list2String(i)
			final.append(i)
		return " ".join(final)

	def _subwriter(self, name, isFeature):
		return FDKSyntaxFeatureWriter(name, isFeature=isFeature)

	def feature(self, name):
		feature = self._subwriter(name, True)
		feature._indentationLevel = self._indentationLevel + 1
		self._instructions.append(feature)
		return feature

	def lookup(self, name):
		lookup = self._subwriter(name, False)
		lookup._indentationLevel = self._indentationLevel + 1
		self._instructions.append(lookup)
		return lookup

	def featureReference(self, name):
		t = "feature %s;" % name
		self._instructions.append(t)

	def lookupReference(self, name):
		t = "lookup %s;" % name
		self._instructions.append(t)

	def classDefinition(self, name, contents):
		t = "%s = [%s];" % (name, self._list2String(contents))
		self._instructions.append(t)

	def lookupFlag(self, rightToLeft=False, ignoreBaseGlyphs=False, ignoreLigatures=False, ignoreMarks=False):
		values = []
		if rightToLeft:
			values.append("RightToLeft")
		if ignoreBaseGlyphs:
			values.append("IgnoreBaseGlyphs")
		if ignoreLigatures:
			values.append("IgnoreLigatures")
		if ignoreMarks:
			values.append("IgnoreMarks")
		if not values:
			values = "0"
		values = ", ".join(values)
		t = "lookupflag %s;" % values
		self._instructions.append(t)

	def gsubType1(self, target, replacement):
		if isinstance(target, list):
			target = "[%s]" % self._list2String(target)
		if isinstance(replacement, list):
			replacement = "[%s]" % self._list2String(replacement)
		t = "sub %s by %s;" % (target, replacement)
		self._instructions.append(t)

	def gsubType3(self, target, replacement):
		if isinstance(target, list):
			target = "[%s]" % self._list2String(target)
		if isinstance(replacement, list):
			replacement = "[%s]" % self._list2String(replacement)
		t = "sub %s from %s;" % (target, replacement)
		self._instructions.append(t)

	def gsubType4(self, target, replacement):
		if isinstance(target, list):
			target = self._list2String(target)
		if isinstance(replacement, list):
			replacement = self._list2String(replacement)
		t = "sub %s by %s;" % (target, replacement)
		self._instructions.append(t)

	def gsubType6(self, precedingContext, target, trailingContext, replacement):
		if isinstance(precedingContext, list):
			precedingContext = self._list2String(precedingContext)
		if isinstance(target, list):
			finalTarget = []
			for t in target:
				if isinstance(t, list):
					t = "[%s]" % self._list2String(t)
				finalTarget.append(t + "'")
			target = " ".join(finalTarget)
		else:
			target += "'"
		if isinstance(trailingContext, list):
			trailingContext = self._list2String(trailingContext)
		if isinstance(replacement, list):
			replacement = self._list2String(replacement)
		# if the replacement is None, this is an "ignore"
		if replacement is None:
			if precedingContext and trailingContext:
				t = "ignore sub %s %s %s;" % (precedingContext, target, trailingContext)
			elif precedingContext:
				t = "ignore sub %s %s;" % (precedingContext, target)
			elif trailingContext:
				t = "ignore sub %s %s;" % (target, trailingContext)
			else:
				t = "ignore sub %s;" % target
		# otherwise it is a regular substitution
		else:
			if precedingContext and trailingContext:
				t = "sub %s %s %s by %s;" % (precedingContext, target, trailingContext, replacement)
			elif precedingContext:
				t = "sub %s %s by %s;" % (precedingContext, target, replacement)
			elif trailingContext:
				t = "sub %s %s by %s;" % (target, trailingContext, replacement)
			else:
				t = "sub %s by %s;" % (target, replacement)
		self._instructions.append(t)

	def gposType1(self, target, value):
		value = "%d %d %d %d" % value
		t = "pos %s <%s>;" % (target, value)
		self._instructions.append(t)

	def gposType2(self, target, value):
		needEnum = False
		left, right = target
		if isinstance(left, list):
			left = "[%s]" % self._list2String(left)
			needEnum = True
		if isinstance(right, list):
			right = "[%s]" % self._list2String(right)
			needEnum = True
		t = "pos %s %s %d;" % (left, right, value)
		if needEnum:
			t = "enum %s" % t
		self._instructions.append(t)

	def languageSystem(self, languageTag, scriptTag):
		t = "languagesystem %s %s;" % (scriptTag, languageTag)
		self._instructions.append(t)

	def script(self, scriptTag):
		t = "script %s;" % scriptTag
		self._instructions.append(t)

	def language(self, languageTag, includeDefault=True):
		if not includeDefault and languageTag != "dflt":
			t = "language %s exclude_dflt;" % languageTag
		else:
			t = "language %s;" % languageTag
		self._instructions.append(t)

	def include(self, path):
		t = "include(%s)" % path
		self._instructions.append(t)

	def subtableBreak(self):
		t = "subtable;"
		self._instructions.append(t)

	def rawText(self, text):
		self._instructions.append(text)

