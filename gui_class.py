import tkinter as tk


class Window(tk.Tk):
	''' Base for a tk window.

	------PARMETERS------
	title (string): title of the window
	width (int): width of the window
	height (int): height of the window
	minwidth (int): lowest allowew width of the window
	minheight (int): lowest allowed height of the window '''

	def __init__(self, title='tk', width=600, height=400, minwidth=500, minheight=300):
		tk.Tk.__init__(self)
		self.title(title)
		self.geometry('{}x{}'.format(width, height))
		self.minsize(minwidth, minheight)

	def darker_bg(self):
		''' returns a slightly darker colour than default background '''
		colour = self['bg'][1:]
		red = int(colour[0:2], 16) - 35
		green = int(colour[2:4], 16) - 35
		blue = int(colour[4:6], 16) - 35
		darker = hex(red)[2:] + hex(green)[2:] + hex(blue)[2:]
		return '#' + darker

class Bar(tk.Entry):
	''' Class for fancier entry widgets.

	------PARAMETERS------
	master (tkinter root): root widget for the entry bar
	default (string): default message displayed on the bar (has to be set)
	**kwarg (various): tkinter arguments for entry widget '''

	def __init__(self, master, default, **kwargs):
		tk.Entry.__init__(self, master, **kwargs, fg='grey', relief='flat')
		self.bind('<FocusIn>', lambda e: self._clear_bar(default))
		self.bind('<FocusOut>', lambda e: self._fill_bar(default))

	def _clear_bar(self, default):
		''' Clears the bar if the user clicks on it '''
		if self.get()==default:
			self.delete('0', 'end')
			self.config(fg='black')

	def _fill_bar(self, default):
		''' Resets bar to default if the user clicks out and it's empty '''
		if self.get()=='':
			self.insert('end', default)
			self.config(fg='grey')
