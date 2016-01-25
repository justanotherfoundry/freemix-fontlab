#FLM: FMX Class Walk
# http://remix-tools.com/freemix
# (C) Tim Ahrens, 2012

from FL import *
import FMX

f = fl.font

markbak = []
for g in fl.font.glyphs:
	markbak.append( g.mark )

class MyDialog:
	def __init__( self ):
		self.d = Dialog( self )
		self.d.size = Point( 280, 400 )
		self.d.Center()
		self.d.title = "FMX Class Walk"
		self.d.AddControl( BUTTONCONTROL, Rect( 70, 10, 120,	 50 ), "minus", STYLE_EDIT, "<" )
		self.d.AddControl( BUTTONCONTROL, Rect( 130, 10, 180,	 50 ), "plus", STYLE_EDIT, ">" )
		self.d.AddControl( STATICCONTROL, Rect( 10, 60, 120,	 88 ), "classname", STYLE_LABEL, " " )
		self.d.AddControl( STATICCONTROL, Rect( 140, 60, 270,	 88 ), "keyglyph", STYLE_LABEL, " " )
		self.d.AddControl( STATICCONTROL, Rect( 10, 90, 260, 320 ), "members", STYLE_LABEL, " " )
		if FMX.classwalk_current > len( f.classes )-1: FMX.classwalk_current = -1
		if FMX.classwalk_current != -1:
			colour_class( FMX.classwalk_current )
			members = ""
			for g in range( 2, len( f.classes[FMX.classwalk_current].split() ) ):
				members += f.classes[FMX.classwalk_current].split()[g] + " "
			self.d.SetLabel( "members",members )
			self.d.SetLabel( "classname",f.classes[FMX.classwalk_current].split()[0][:-1] )
			self.d.SetLabel( "keyglyph",f.classes[FMX.classwalk_current].split()[1][:-1] )
	def on_minus( self, code ):
		if FMX.classwalk_current < 1: FMX.classwalk_current = len( f.classes )-1
		else: FMX.classwalk_current -= 1
		colour_class( FMX.classwalk_current )
		members = ""
		for g in range( 2, len( f.classes[FMX.classwalk_current].split() ) ):
			members += f.classes[FMX.classwalk_current].split()[g] + " "
		self.d.SetLabel( "members",members )
		self.d.SetLabel( "classname",f.classes[FMX.classwalk_current].split()[0][:-1] )
		self.d.SetLabel( "keyglyph",f.classes[FMX.classwalk_current].split()[1][:-1] )
	def on_plus( self, code ):
		if FMX.classwalk_current == len( f.classes )-1: FMX.classwalk_current = 0
		else: FMX.classwalk_current += 1
		colour_class( FMX.classwalk_current )
		members = ""
		for g in range( 2, len( f.classes[FMX.classwalk_current].split() ) ):
			members += f.classes[FMX.classwalk_current].split()[g] + " "
		self.d.SetLabel( "members",members )
		self.d.SetLabel( "classname",f.classes[FMX.classwalk_current].split()[0][:-1] )
		self.d.SetLabel( "keyglyph",f.classes[FMX.classwalk_current].split()[1][:-1] )
	def on_ok( self, code ):
		return 1
	def Run( self ):
		return self.d.Run()


def colour_class( c ):
	for g in fl.font.glyphs:
		if g.mark != 0:
			g.mark = 0
	for g in range( 1, len( f.classes[c].split() ) ):
			if f.classes[c].split()[g][-1:] == "'":
					index = f.FindGlyph( f.classes[c].split()[g][:-1] )
					f[index].mark = FMX.MARK_KEY
			else:
					index = f.FindGlyph( f.classes[c].split()[g] )
					if ( f.GetClassRight( c ) and f.GetClassLeft( c ) ) or ( f.GetClassMetricsFlags( c )[0] and f.GetClassMetricsFlags( c )[1] )	or f.GetClassMetricsFlags( c )[2]:
							f[index].mark = FMX.MARK_MEMBER
					elif f.GetClassLeft( c ) or f.GetClassMetricsFlags( c )[0]:
							f[index].mark = FMX.MARK_LEMON
					elif f.GetClassRight( c ) or f.GetClassMetricsFlags( c )[1]:
							f[index].mark = 4
	fl.UpdateFont()


d = MyDialog()
if d.Run() == 1:
	f.modified = 1
else:
	for g in range( len( fl.font.glyphs ) ):
		f[g].mark = markbak[g]
	fl.UpdateFont()
