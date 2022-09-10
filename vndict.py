from bs4 import BeautifulSoup
import requests, lxml


def vndict(query):
	
	vtudien_url = "https://vtudien.com/viet-viet/dictionary/nghia-cua-tu-" + query
	soha_url = "http://tratu.soha.vn/dict/vn_vn/" + query.replace(" ", "_");

	try:
		html = requests.get(vtudien_url).text
		soup = BeautifulSoup(html, 'lxml')
		box = soup.select_one('.td-content, .td-bktt, .td-mrth').text
		return(box)
	except AttributeError:
		try:
			html = requests.get(soha_url).text
			soup = BeautifulSoup(html, 'lxml')
			boxes = soup.find_all("span", {"class":"mw-headline"})
			box = '\n'.join(individual.string.strip() for individual in boxes) 
			return(box)
		except AttributeError:
			return("Entry not found.")