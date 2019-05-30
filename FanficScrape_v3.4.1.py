#!/usr/bin/env python3
import time
import tkinter as tk
import gui_class as gui
from thread_class import Thread
from tkinter import filedialog

#------ DEFINE ------
def clear_output_folder():
	''' Clears the 'Output/' directory '''
	import os

	for file in os.listdir('Output'):
		file_path = os.path.join('Output', file)
		try:
			if os.path.isfile(file_path):
				os.unlink(file_path)
		except Exception as e:
			print(e)

def get_fic(url, path='Output/', textbox=None, mode=False, count=False, pretty=True):
	''' Prints each threadmarked chapter into an html file.

	------ARGUMENTS------
	url (string): the XenForo url of the thread to be downloaded
	path (string): the path where the files will be downloaded to
	textbox (tk.Text): the function prints statuses into this tkinter textbox
	mode (boolean):
		boolean value uset to decide whether to try downloading the thread
		from its reader mode (reader mode could not work for centain threads)
	count (boolean):
		boolean value to decide whether to add a chapter counter to the
		beginning of each file name
	pretty (boolean):
		boolean value used to decide wether to make the XenForo standard html
		more ebook-freindly '''
	
	# Init
	if count:
		counter = 0
	else:
		counter = None

	time1 = time.time()

	try:
		thread = Thread(url, mode)
	except Exception as e:
		if textbox is not None:
			update_text(textbox, 'There has been a problem.\nPlease try again.\n\n{}'.format(e))
		return 0
	else:
		clear_output_folder()
		chapter_title = thread.chapter_title(thread.first_title, counter)

	for i, page in enumerate(thread.pages):

		sections = thread.slice_page(page)								# Slice webpage in sections (one each post)
		
		for section in sections:									# Evaluate each section

			threadmark = section.find("span", class_="label")					# Find if the post contains a new chapter
			message = thread.pull_content(section)							# Find if the post contains a message

			if threadmark is not None:
				if count:
					counter += 1

				if chapter_title is not None:
					thread.add_closers(path, chapter_title)					# Wrap up previous file
					if pretty:
						thread.prettify(path, chapter_title)

				chapter_title = thread.chapter_title(threadmark, counter)			# Set the name of the next chapter
				
				thread.add_headers(path, chapter_title, thread.title)				# Open new file with new name

			if message is not None:
				thread.add_content(path, chapter_title, message)				# Add content of message to file

	thread.add_closers(path, chapter_title)									# Close last file
	if pretty:
		thread.prettify(path, chapter_title)

	time2 = time.time()

	if textbox is not None:
		update_text(textbox, '"' + thread.title + '"' + ' finished in {:.2f}ms ...\n\nReady'.format(time2-time1))

def get_path(path):
	''' Updates download path '''
	newpath = filedialog.askdirectory(initialdir="Output/", title="Select directory")
	path.set(newpath)

def update_text(textbox, string):
	''' Updates the message inside the textbox widget '''
	textbox.config(state='normal')
	textbox.delete('1.0', 'end')
	textbox.insert('end', string)
	textbox.config(state='disabled')

def window():
	#------ INIT ------
	# Window
	window = gui.Window(title='Fanfic Scrape', width=700, height=480, minwidth=600, minheight=480)
	
	# Misc
	url = tk.StringVar(value='Insert the address here')
	path = tk.StringVar(value='Output/')
	mode = tk.BooleanVar()
	count = tk.BooleanVar()
	pretty = tk.BooleanVar()

	#----- WINDOW SETUP ------
	base = tk.Frame(window)
	base.pack(expand='yes', fill='both', padx=20, pady=20)

	# Output
	output = tk.Frame(base, bg=window.darker_bg())
	output.pack(anchor='n', fill='x', pady=20, padx=20)

	path_label = tk.Label(output, text='Destination folder: ', bg=window.darker_bg())
	path_label.pack(side='left')

	path_bar = gui.Bar(output, path.get(), textvariable=path)
	path_bar.pack(side='left', expand='yes', fill='x', pady=4, padx=4)

	path_button = tk.Button(output,
		text='Explore',
		bg=window.darker_bg(),
		relief='flat',
		command=lambda: get_path(path))
	path_button.pack(side='right')

	# Search
	search = tk.Frame(base, bg=window.darker_bg())
	search.pack(anchor='n', fill='x', pady=20, padx=20)

	bar_title = tk.Label(search, text='Thread URL: ', bg=window.darker_bg())
	bar_title.pack(side='left', pady=5, padx=4)

	url_bar = gui.Bar(search, url.get(), textvariable=url)
	url_bar.pack(expand='yes', fill='x', padx=4)
	
	# Options
	options = tk.Frame(base)
	options.pack(fill='both', padx=20)

	numbers = tk.Checkbutton(options,
		text="Add chapter number at the beggining of the file name",
		variable=count, onvalue=True, offvalue=False)
	numbers.select()
	numbers.pack(anchor='w')

	reader = tk.Checkbutton(options,
		text="Try reader mode: avoids user comments and all non-threadmarked posts\n(breaks story-only threads)",
		variable=mode, onvalue=True, offvalue=False, height=2, justify='left')
	reader.select()
	reader.pack(anchor='w')

	prettify = tk.Checkbutton(options,
		text="Try to improve the html of the file (beta)",
		variable=pretty, onvalue=True, offvalue=False)
	prettify.select()
	prettify.pack(anchor='w')

	# Text output
	out_frame = tk.Frame(base)
	out_frame.pack(side='bottom', fill='x', pady=20, padx=20)

	textframe = tk.Frame(out_frame)
	textframe.pack(side='bottom', fill='x', pady=20)

	feedback = tk.Text(textframe, height=5, bg='#708090', fg='turquoise', wrap='word')
	update_text(feedback, 'Ready')
	feedback.pack(expand='yes', fill='x')

	# Fetch content
	fetch = tk.Frame(out_frame)
	fetch.pack(anchor='s', expand='yes', fill='x')

	fetch_button = tk.Button(fetch,
		text='GET',
		command=lambda: get_fic(
			url=url.get(),
			path=path.get(),
			textbox=feedback,
			mode=mode.get(),
			count=count.get(),
			pretty=pretty.get()))
	fetch_button.pack(fill='x')

	window.mainloop()

if __name__=='__main__':
	window()
