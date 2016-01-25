Freemix Tools for FontLab
=======

Some Python scripts to be used with [FontLab](http://www.fontlab.com/).

To install, just download [FMX 1.0 installer.flw](https://github.com/justanotherfoundry/freemix-fontlab/raw/master/FMX%201.0%20installer.flw) and open it with FontLab Studio.

FMX Glyph Table

-     This tool currently only works in FontLab 5.1 on Mac OS.
-     This is an attempt to represent all glyph-specific data in the font in an editable table.
-     To copy the data into the clipboard, run the macro in the Font Window with some glyphs selected, or no selection, which copies the whole font.
-     Try pasting the clipboard into a spreadsheet application like Excel or Numbers.
-     For built-in documentation, select “add help row”.
-     Some columns are editable: modify, copy back to the clipboard, and “paste” in FontLab by running the macro again.
-     The tool reports all changes it makes to the font (except mark and selection). While the tool is still a bit experimental, I am confident that this particular functionality is reliable: The tool will not make any changes behind your back.
-     In order to rename glyphs (i.e. modifying the base name or extension column), you need to include the index column.
-     If the index column is not pasted, the tool identifies glyphs by name, which allows you to quickly apply changes to several fonts.
-     Pasting non-editable columns does not hurt – they will be ignored.
-     Some columns support meta values such as (base comp) or (base name).
-     Screen cast coming soon.

FMX Class Walk

-     Step through your classes and see live marking of the key glyph (blue) and members.
-     The members are marked red for R classes, yellow for L classes, and orange for R&L classes.
-     Break off with OK to resume the walk at the same class later.

FMX Mark Classes

-     Marks the key glyphs of all classes blue and all members orange.
-     Gives warnings if glyphs are keys or members for multiple classes.
-     By default, this tool shows the kerning classes. In the macro code, change class_start to '.' show metrics classes.

FMX Stem Histogram

-     Inspired by Peter Karow’s method, it visualizes which stem weights occur in the font.
-     This tool merely analyzes the hints and links, it does not detect stems.
-     Select a number of glyphs, or none to output the whole font.
-     The histogram can be useful when defining standard stems.
-     You can use it to detect inconsistent stem weights.
-     The histrogram reveals wrongly set hints as they are often created by autohinting when it catches whole terminals as stems.

FMX Kerning/Metrics class

-     Select a glyph in the font window, right-click and choose from the Macro submenu.
-     This sets up a kerning or metrics class, which you will find in the Classes panel.

FMX Mark

-     Select some glyphs in the font window, right-click and choose your color.

FMX Select same Color/Suffix

-     Access by right-clicking in the Font Window.
-     Selects all other glyphs with the glyph’s color or suffix (i.e. separated by '.').


Released under the MIT License.