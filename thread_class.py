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

	def __init__(self, url, mode=False):
		self.list = self._list_of_URLs(url, mode)
		self.pages = self._pages_list(self.list)
		# self.pages = pagelist
		self._check_url(self.pages)
		self.title = self._thread_title(self.pages)
		self.first_title = self._first_chapter_title(self.pages)

	# Internal
	def _list_of_URLs(self, start_url, mode):
		''' Takes the URL of the first page of the forum.
		Returns a list of all the URLs in the thread '''
		pagelist  = [start_url] #the first URL stays unchanged
		page      = requests.get(start_url)
		soup      = BeautifulSoup(page.text, 'lxml')
		body      = soup.body
		last_page = int(body.find('div', class_="PageNav")['data-last'])

		if mode==True:
			if start_url[-6:]=='reader':
				if start_url[-7:]!='/reader':
					start_url += '/reader' 
			if start_url[-6:]!='reader':
				if start_url[-1]!='/':
					start_url += '/reader'
				else:
					start_url += 'reader'

		if start_url[-7:]!='/reader' and start_url[-1]=='/':
			pagelist += [start_url + 'page-' + str(i + 1) for i in range(1, last_page)] #usually
		elif start_url[-1]!='/':
			pagelist += [start_url + '/page-' + str(i + 1) for i in range(1, last_page)]
		else:
			pagelist += [start_url + '?page=' + str(i + 1) for i in range(1, last_page)] #if the URL points to reader mode

		return pagelist

	def _pages_list(self, URLs):
		''' Takes the list of all pages in a thread.
		Returns the pages as bs4 objects '''
		pages = []

		for i, page in enumerate(URLs):
			html = requests.get(page)
			soup = BeautifulSoup(html.text, 'lxml')
			pages.append(soup.body)
		
		return pages

	def _fix_title(self, title, file_mode=True):
		''' Changes a chapter name to a valid file name and back '''
		if title is not None:
			import re

			if file_mode:
				title = re.sub(' ', '_', title)
				title = re.sub('/', '×', title)
				title = re.sub(r'\.', '˛', title)
				title = re.sub(r'\?', '~', title)
				title = re.sub(': ', '–', title)
				return title
			else:
				title = re.sub('_', ' ', title)
				title = re.sub('×', '/', title)
				title = re.sub('˛', r'\.', title)
				title = re.sub('~', r'\?', title)
				title = re.sub('–', ': ', title)
				return title
		return title

	def _thread_title(self, pages):
		''' Takes the list of pages in the thread.
		Returns the title of the thread '''
		for page in pages:
			thread_title = page.find('h1')
			thread_title = thread_title.get_text()
		
		return thread_title

	def _first_chapter_title(self, pages):
		''' Takes the list of pages in the thread.
		Searches for the first page for a threadmark.
		Returns the threadmark's text content as a title.
		
		Asks the user to input a title if none is found.'''
		chapter_title = None
		threadmark = pages[0].find("span", class_="label")

		if threadmark is not None:
			return None
		else:
			chapter_title = self._fix_title(title)
			return chapter_title

	def _check_url(self, pages):
		''' Checks if the given URL is usable '''
		for page in pages:
			if page.find('li', class_="message") is None:
				raise TypeError("Unexpected webpage format, unable to find section markers")
			if page.find("blockquote",class_="messageText SelectQuoteContainer ugc baseHtml") is None:
				raise TypeError("No posts were found in this thread")

	# External
	def chapter_title(self, threadmark_tag, counter=None):
		''' Takes a bs4 object (a section from the page), possibly a chapter counter.
		Returns the chapter's name if the tag had a content, else returns 'None'. ''' 
		try:
			label = threadmark_tag.get_text()
			title = label[14:-3]
		except:
			title = threadmark_tag

		if counter is not None and title is not None:
			chapter_title = 'Chapter_{}–{}'.format(counter, self._fix_title(title))
		elif title is not None:
			chapter_title = self._fix_title(title)
		else:
			chapter_title = None
		return chapter_title

	def add_headers(self, path, chapter, title):
		''' Adds html headers at the beginning of the file '''
		chapter_name = self._fix_title(chapter, file_mode=False)
		with open(path + chapter + '.html', 'w+') as file:
			file.write(
				'<!DOCTYPE html>\n'
				+ '<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">\n'
				+ '<head>\n'
				+ '<meta charset="utf-8"/>\n'
				+ '<title>' + title + '</title>\n'
				+ '</head>\n<body>\n\n'
				+ '<h2>' + chapter_name + '</h2>'
				)

	def add_closers(self, path, chapter):
		''' Add html closers to end of file '''
		with open(path + chapter + '.html', 'a') as file:
			file.write('</body>\n</html>')

	def add_content(self, path, chapter, body):
		''' Adds the contents of the post to file '''
		with open(path + chapter + '.html', 'a') as file:
			for content in body.contents:
				file.write(str(content))
			file.write('<hr/>\n')

	def slice_page(self, page):
		''' Takes page bs4 object, returns list of XenForo sections (marked as 'li') '''
		sections = page.find_all('li', class_='message')
		return sections

	def pull_content(self, section):
		''' Takes a user post, returns its text content '''
		content = section.find("blockquote", class_="messageText SelectQuoteContainer ugc baseHtml")
		return content

	def prettify(self, path, chapter):
		''' Prettifies the html of a file '''
		import re

		tags = ['i', 'b', 'a', 'li', 'span']

		with open(path + chapter + '.html', 'r') as file:
			text = file.read()
			
		text = re.sub('\t\t\t\t\t\n\t\t\t\t\t', '<p>', text)
		text = re.sub('<div class="messageTextEndtags"> </div>', '</p>', text)
		text = re.sub('<br/>\n<br/>\n<br/>\n<br/>', '<hr/>', text)

		for i in tags:
			text = re.sub('<br/>\n<{}>'.format(i), '<{}>'.format(i), text)
			text = re.sub('<br/>\n</{}>'.format(i), '</{}>'.format(i), text)
			text = re.sub('<{}>\n<br/>'.format(i), '<{}>'.format(i), text)
			text = re.sub('</{}>\n<br/>'.format(i), '</{}>'.format(i), text)

		text = re.sub('<br/>', '</p>\n<p>', text)
		text = re.sub('<p>\n', '<p>', text)
		text = re.sub('\n</p>', '</p>', text)
		text = re.sub('<p></p>', '', text)

		for i in tags:
			text = re.sub('<p><{}></{}></p>'.format(i, i), '', text)
			text = re.sub(r'<p><{}.*> </{}></p>'.format(i, i), '', text)

		for i in tags:
			text = re.sub('<{}><{}>'.format(i, i), '', text)
			if i!='span':
				text = re.sub('</{}></{}>'.format(i, i), '', text)

		text = re.sub(r'\&', '&amp;', text)

		if text.find('<p>')>text.find('</p>'):
			if text.find('</h2>')<text.find('</p>'):
				text = re.sub('</h2>', '</h2>\n<p>', text)

		text = re.sub('<p>\n', '<p>', text)
		text = re.sub('\n</p>', '</p>', text)
		text = re.sub('<p></p>', '', text)

		with open(path + chapter + '.html', 'w') as file:
			file.write(text)
