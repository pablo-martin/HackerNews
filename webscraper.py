import os
import time
import pickle
import datetime
import urllib2
from bs4 import BeautifulSoup

base_url = 'https://news.ycombinator.com/'
main_url = 'https://news.ycombinator.com/newest'
hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}
old_hdr = {'User-Agent': 'Mozilla/5.0'}
ROOT = os.environ['HOME'] + '/python/HackerNews/'


def get_my_soup(url):
    response = urllib2.Request(url, headers=hdr)
    try:
        html = urllib2.urlopen(response)
        soup = BeautifulSoup(html, 'html.parser')
    except urllib2.HTTPError:
        soup = None
    return soup

def extract_headlines(soup):
    links = soup.find_all('a')
    links_class = [w for w in links if 'class' in w.attrs.keys()]
    headlines = \
        [w.string for w in links_class if w.attrs['class'][0] == 'storylink']

    next_page = [w for w in links_class if w.attrs['class'][0] == 'morelink']
    next_url = base_url + next_page[0].attrs['href']
    return headlines, next_url

def single_scrape():
    current_time = unicode(datetime.datetime.now())
    print('Scraping website at %s' %current_time)
    scheduler = pickle.load(open(ROOT + 'scheduler.p','rb'))
    HEADLINES = []
    soup = get_my_soup(main_url)
    while soup is not None:
        print('scraping another webpage...')
        headlines, next_url = extract_headlines(soup)
        HEADLINES += [unicode(w) for w in headlines]
        soup = get_my_soup(next_url)
    #drop duplicates
    HEADLINES = list(set(HEADLINES))

    old_headlines = pickle.load(open(ROOT + 'headlines.p','rb'))
    new_headlines = list(set(HEADLINES) - \
                         set(old_headlines).intersection(set(HEADLINES)))
    old_headlines += new_headlines
    pickle.dump(old_headlines, open(ROOT + 'headlines.p','wb'))
    print('added %i new headlines:' %len(new_headlines))
    for new_news in new_headlines:
        print(('\t'+ new_news).encode('utf8'))
    print('we have a total of %i headlines' %(len(old_headlines)))
    scheduler[current_time] = new_headlines
    pickle.dump(scheduler, open(ROOT + 'scheduler.p','wb'))


if __name__ == '__main__':
    single_scrape()
