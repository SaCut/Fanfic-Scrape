# #!/usr/bin/python
# print('Content-type: text/html\r\n\r')

from bs4 import BeautifulSoup
import requests

# init
counter = 0
chapterName = None


# produce a /Output/chapter.html label for each chapter
def find_label(chapter, counter):
    label = chapter.get_text()
    title = label[14:-3]
    filename = "Output/{} {}.html".format(counter, title)
    return filename


# produce a list of all the pages of the thread
def page_num(url):
    pages = [url]
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "lxml")
    body = soup.body
    last_page = int(body.find('div', class_="PageNav")['data-last'])
    pages += [url + 'page-' + str(i + 1) for i in range(1, last_page)]
    return pages


# List of all the pages of the thread
List = page_num(input('Insert the URL of a thread: '))

# main loop
for i, page in enumerate(List):

    # get source
    page = requests.get(page)
    # soupify
    soup = BeautifulSoup(page.text, "lxml")
    body = soup.body

    # thread title
    fullTitle = body.find('h1')
    fullTitle = fullTitle.get_text()

    # first title
    if i == 0:
        try:
            TitleSection = body.find("span", class_="label")
            chapterName = find_label(TitleSection, 1)

        except Exception:
            print("Unable to find threadmark in first page")
            chapterName = "Output/{} {}.html".format(1, input('Choose a name for the first chapter: '))

    # find all sub-sections in page
    Sections = body.find_all('li')

    # evaluate each section
    for j, li in enumerate(Sections):

        # if there is threadmark in section
        chapter = li.find("span", class_="label")
        if chapter is not None:
            counter += 1

            # wrap up previous file
            with open(chapterName, 'a') as file:
                file.write(' </body>\n'
                           '</html>')

            # Isolate name of thread
            chapterName = find_label(chapter, counter)

            # write chapter name to file
            with open(chapterName, 'w+') as file:
                # write html headers
                file.write('<!DOCTYPE html>\n'
                           '<html lang="en-US">\n'
                           ' <head>\n'
                           '  <meta charset="utf-8"/>\n'
                           '  <title>' + fullTitle + '</title>\n'
                           ' </head>\n'
                           ' <body>\n')

                # find content of threadMarked post
                scan = li.find('blockquote', class_="messageText SelectQuoteContainer ugc baseHtml")

        # if there is post content in section
        chapter = li.find("blockquote", class_="messageText SelectQuoteContainer ugc baseHtml")
        if chapter is not None and chapterName is not None:

            # write post content to file
            with open(chapterName, 'a') as file:
                for content in chapter.contents:
                    file.write(str(content))

                # add a cool separator between posts
                file.write('<hr noshade="noshade" size="2"/>\n')
