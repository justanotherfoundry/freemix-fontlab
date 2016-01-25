#FLM: FMX Glyph Table
# http://remix-tools.com/freemix
# (C) Tim Ahrens, 2012

from FL import *

while fl.font != None:
	import FMX_glyph_table_copy
	import FMX_glyph_table_paste
	try:
		import os, MacOS
		import wx
		use_wx = True
	except ImportError:
		try:
			from Carbon.Scrap import GetCurrentScrap, ClearCurrentScrap
			use_wx = False
		except ImportError:
			fl.Message( 'Sorry, this macro is currently only available for Mac OS.' )
			break

	# get clipboard
	if use_wx:
		try:
			clip = wx.Clipboard()
		except:
			dummy = wx.App(0)
			clip = wx.Clipboard()
		text = wx.TextDataObject()
		clip.Open()
		clip.GetData( text )
		clip.Close()
		clip_rows = text.GetText().encode( 'utf-8' ).splitlines()
	else:
		try:
			clip_rows = GetCurrentScrap().GetScrapFlavorData( 'utf8' ).splitlines()
		except ( TypeError, MacOS.Error ):
			try:
				clip_rows = GetCurrentScrap().GetScrapFlavorData( 'TEXT' ).splitlines()
			except ( TypeError, MacOS.Error ):
				clip_rows = ['']
	if clip_rows:
		clip_columns = clip_rows.pop(0).split('\t')
		if 'base name' in clip_columns:
			dialog = FMX_glyph_table_paste.FMXdialog()
			dialog.select_master( FMX_glyph_table_copy.dialog_selected_master )
			if dialog.d.Run() == 1:
				fl.output = ''
				print 'Pasting table\n'
				FMX_glyph_table_paste.paste_table( clip_columns, clip_rows, fl.font, dialog.selected_master )
				print '\nDone.'
				break

	# dialog for copy
	dialog = FMX_glyph_table_copy.FMXdialog( FMX_glyph_table_copy.dialog_selection )
	dialog.select_master( FMX_glyph_table_copy.dialog_selected_master )
	if dialog.d.Run() != 2:
		FMX_glyph_table_copy.dialog_selection = dialog.selection
		FMX_glyph_table_copy.dialog_selected_master = dialog.selected_master
		# write to clipboard
		if use_wx:
			text = wx.TextDataObject( dialog.string )
			# clip = Clipboard()
			clip.Open()
			clip.SetData( text )
			clip.Close()
		else:
			ClearCurrentScrap()
			GetCurrentScrap().PutScrapFlavor( 'utf8', 0, dialog.string.encode( 'utf8' ) )
	break
