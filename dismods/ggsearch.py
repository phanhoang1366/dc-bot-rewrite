from bs4 import BeautifulSoup
import requests, lxml
from googlesearch import search

headers = {
    'User-agent':
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:101.0) Gecko/20100101 Firefox/101.0"
}

def gsearch(you):

	#updated_query = you.replace(" ", "+")
	google_url = "https://www.google.com.vn/search?q=" + you

	html = requests.get(google_url, headers=headers).text
	soup = BeautifulSoup(html, 'lxml')
	try:
		box = soup.select_one(' .hgKElc b, .d9FyLd b, .IZ6rdc, .EfDVh, .mw31Ze').text
		return(box)
	except AttributeError:
		try:
			box = soup.select_one('.kno-rdesc').find_all('span')[0].text
			return(box)
		except AttributeError:
			for j in search(you, num_results=1):
				return(j)