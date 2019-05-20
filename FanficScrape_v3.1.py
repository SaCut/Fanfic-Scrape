#!/usr/bin/env python3
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

def get_fic(url, path='Output/', textbox=None, mode=None):
	''' Prints each threadmarked chapter into an html file.

	------ARGUMENTS------
	url (string): the XenForo url of the thread to be downloaded
	path (string): the path where the files will be downloaded to
	textbox (tk.Text): the function prints statuses into this tkinter textbox
	mode (tk.Boolean):
		boolean value uset to decide whether to try downloading the thread
		from its reader mode (reader mode can not exist) '''
	
	# Init
	counter = 1
	try:
		thread = Thread(url, mode)
	except Exception as e:
		if textbox is not None:
			update_text(textbox, e)
		return('stop')
	else:
		clear_output_folder()

	for i, page in enumerate(thread.pages):

		if i == 0:
			chapter_title = thread.first_title											# Set first title

			thread.add_headers(path, chapter_title, thread.title)				# Initialise chapter with headers

		sections = thread.slice_page(page)							# Slice webpage in sections (one each post)
		
		for _, section in enumerate(sections):							# Evaluate each section

			threadmark = section.find("span", class_="label")				# Find if the post contains a new chapter

			if threadmark is not None:
				counter += 1

				thread.add_closers(path, chapter_title)					# Wrap up previous file

				chapter_title = thread.chapter_title(threadmark, counter)		# Set the name of the next chapter

				thread.add_headers(path, chapter_title, thread.title)			# Write new chapter name to file

			message = thread.pull_content(section)						# Search for a post in each section
			if message is not None:

				with open(path + chapter_title, 'a') as file:				# Write post content to file
					for content in message.contents:
						file.write(str(content))
					
					file.write('<hr noshade="noshade" size="2"/>\n')		# Add a cool separator between posts

	if textbox is not None:
		update_text(textbox, '"' + thread.title + '"' + ' finished\n\nready')

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

def main():

	#------ INIT ------
	# Window
	window = gui.Window(title='Fanfic Scrape', width=700, height=450, minwidth=600, minheight=450)
	
	# Misc
	url = tk.StringVar(value='Insert the address here')
	path = tk.StringVar(value='Output/')
	mode = tk.BooleanVar(value=False)

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

	mode = tk.Checkbutton(options,
		text="Try to read thread in reader mode (without non-threadmarked posts)",
		variable=mode, onvalue=True, offvalue=False)
	mode.pack(side='left', fill='x')

	#TODO add options

	# Text output
	out_frame = tk.Frame(base)
	out_frame.pack(side='bottom', fill='x', pady=20, padx=20)

	textframe = tk.Frame(out_frame)
	textframe.pack(side='bottom', fill='x', pady=20)

	feedback = tk.Text(textframe, height=5, bg='#708090', fg='turquoise', wrap='word')
	update_text(feedback, 'ready')
	feedback.pack(expand='yes', fill='x')

	# Fetch content
	fetch = tk.Frame(out_frame)
	fetch.pack(anchor='s', expand='yes', fill='x')

	fetch_button = tk.Button(fetch,
		text='GET',
		command=lambda: get_fic(url=url.get(), path=path.get(), textbox=feedback))
	fetch_button.pack(fill='x')

	window.mainloop()

if __name__=='__main__':
	main()
