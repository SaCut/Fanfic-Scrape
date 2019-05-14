#!/usr/bin/env python3

import os
from object import Thread

#------CLEAR------
def ClearOutputFolder():
	''' Clear 'Output/' directory '''
	for file in os.listdir('Output'):
	    file_path = os.path.join('Output', file)
	    try:
	        if os.path.isfile(file_path):
	            os.unlink(file_path)
	    except Exception as e:
	        print(e)

#------ MAIN ------
def main():
	#------ INIT ------
	counter = 1
	# url = str(input('Insert the URL of the thread you want to download: ')))
	url = 'https://forums.spacebattles.com/threads/burn-up-worm-complete.395526/reader'
	thread = Thread(url)

	ClearOutputFolder()

	for i, page in enumerate(thread.pages):

		if i == 0:														# Set first title 
			chapter_path = thread.first_title

			thread.add_headers(chapter_path, thread.title)				# Initialise chapter with headers

		sections = thread.slice_page(page)								# Slice webpage in sections
		
		for _, section in enumerate(sections):							# Evaluate each section

			threadmark = section.find("span", class_="label")			# Find the name of the current chapter

			if threadmark is not None:
				counter += 1

				thread.add_closers(chapter_path)						# Wrap up previous file

				chapter_path = thread.chapter_path(threadmark, counter)	# Set the name of the next chapter

				thread.add_headers(chapter_path, thread.title)			# Write new chapter name to file

			message = thread.pull_content(section)						# Search for a post in each section
			if message is not None:

				with open(chapter_path, 'a') as file:					# Write post content to file
					for content in message.contents:
						file.write(str(content))
					
					file.write('<hr noshade="noshade" size="2"/>\n')	# Add a cool separator between posts

	print('"' + thread.title + '"' + ' finished')

if __name__=='__main__': main()