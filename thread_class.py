import requests
from bs4 import BeautifulSoup
from lxml import html

class Thread():
	''' Class to parse a XenForo thread.
	
	------PARAMETERS------
	url (string):
		url from the first page of a XenForo thread
		(tested only with spacebattles/sufficientvelocity)
		doesn't work with log-in required
		
	------ATTRIBUTES------
	list (list): list of URLs obtained from the first URL
	pages (list): list of all webpages from thread in bs4-object form
	title (string): the title of the whole thread
	first_title (string): the title of the first threadmark. '''

	def __init__(self, url):
		self.list = self._list_of_URLs(url)
		self.pages = self._pages_list(self.list)
		self._check_url(self.pages)
		self.title = self._thread_title(self.pages)
		self.first_title = self._first_chapter_title(self.pages)

	# Internal
	def _list_of_URLs(self, start_url):
		''' Takes the URL of the first page of the forum.
		Returns a list of all the URLs in the thread '''
		pagelist  = [start_url] #the first URL stays unchanged
		page      = requests.get(start_url)
		soup      = BeautifulSoup(page.text, "lxml")
		body      = soup.body
		last_page = int(body.find('div', class_="PageNav")['data-last'])

		if start_url[-6:]!='reader':
			pagelist += [start_url + 'page-' + str(i + 1) for i in range(1, last_page)] #usually
		else:
			pagelist += [start_url + '?page=' + str(i + 1) for i in range(1, last_page)] #if the URL points to reader mode

		return pagelist

	def _pages_list(self, URLs):
		''' Takes the list of all pages in a thread.
		Returns the pages as bs4 objects '''
		pages = []

		for i, page in enumerate(URLs):
			html = requests.get(page)
			soup = BeautifulSoup(html.text, "lxml")
			pages.append(soup.body)
		
		return pages

	def _thread_title(self, pages):
		''' Takes the list of pages in the thread.
		Returns the title of the thread '''
		for page in pages:
			thread_title = page.find('h1')
			thread_title = thread_title.get_text()
		
		return thread_title

	def _first_chapter_title(self, pages):
		''' Takes the list of pages in the thread.
		Searches for the first occurrence of a threadmark.
		Calls chapter_title().
		Returns the threadmark's text content as a title.
		
		Asks the user to input a title if none is found.'''
		chapter_path = None

		for page in pages:
			try:
				threadmark = page.find("span", class_="label")
				chapter_path  = chapter_path(threadmark, 1)
				return chapter_path
				break
			except Exception:
				continue
		
		if chapter_path is None:
			chapter_path = "Chapter_1–{}".format(str(self.title).replace(' ', '_').replace('/', ';'))
			return chapter_path

	def _check_url(self, pages):
		''' Checks if the given URL is usable '''
		for i, page in enumerate(pages):
			if page.find('li', class_='message') is None:
				raise TypeError("Unexpected webpage format, unable to find section markers")
			if page.find("blockquote",class_="messageText SelectQuoteContainer ugc baseHtml") is None:
				raise TypeError("No posts were found in this thread")

	# External
	def chapter_title(self, threadmark_tag, counter):
		''' Takes a bs object (a section from the page) and a counter.
		Returns the chapter's name. '''
		import os
		label = threadmark_tag.get_text()
		title = label[14:-3]
		chapter_title = 'Chapter_{}–{}'.format(counter, title.replace(' ', '_').replace('/', ';'))
		return chapter_title

	def add_headers(self, path, chapter, title):
		''' Adds html headers at the beginning of the file '''
		chapter_name = chapter.replace('_', ' ').replace('–', ':').replace(';', '/')
		with open(path + chapter, 'w+') as file:
			file.write(
				'<!DOCTYPE html>\n<html lang="en-US">\n <head>\n'
				+ '<meta charset="utf-8"/>\n<title>'
				+ '<h1>' + title + '</h1>'
				+ '</title>\n</head>\nbody>\n\n'
				+ '<h2>' + chapter_name + '<h2>'
				)

	def add_closers(self, path, chapter):
		''' Add html closers to end of file '''
		with open(path + chapter, 'a') as file:
			file.write('</body>\n</html>')

	def slice_page(self, page):
		''' Takes page bs4 object, returns list of XenForo sections (marked as 'li') '''
		sections = page.find_all('li', class_='message')
		return sections

	def pull_content(self, section):
		''' Takes a user message, returns its text content '''
		content = section.find("blockquote", class_="messageText SelectQuoteContainer ugc baseHtml")
		return content
