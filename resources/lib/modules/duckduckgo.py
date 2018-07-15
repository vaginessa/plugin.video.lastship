from resources.lib.modules import client
from resources.lib.modules import dom_parser
from resources.lib.modules import cleantitle
from resources.lib.modules import source_faultlog
from resources.lib.modules import source_utils
import re

base_url = 'https://duckduckgo.com/html'

def cleanhtml(raw_html):
  cleanr = re.compile('<.*?>')
  cleantext = re.sub(cleanr, '', raw_html)
  return cleantext


def search(titles, year, site, titleRegex):
    try:
        params = {
            'q': '%s site:%s' % (titles[0], site),
            's': '0'
        }

        result = client.request(base_url, post=params, headers={'Content-Type': 'application/x-www-form-urlencoded'}, error=True)
        if params['q'] not in result.lower():
            links = dom_parser.parse_dom(result, 'h2', attrs={'class': 'result__title'})
            links = dom_parser.parse_dom(links, 'a')
            links = [(client.replaceHTMLCodes(i.content), i.attrs['href']) for i in links if site in i.attrs['href']]

            links = [(re.findall(titleRegex, i[0])[0], i[1]) for i in links if re.search(titleRegex, i[0]) is not None]
            links = [(cleanhtml(i[0]), i[1], year in i[1]) for i in links]

            links = sorted(links, key=lambda i: i[2], reverse=True)  # with year > no year

            t = [cleantitle.get(i) for i in set(titles) if i]

            links = [i[1] for i in links if cleantitle.get(i[0]) in t]

            if len(links) > 0:
                return source_utils.strip_domain(links[0])

        return
    except:
        source_faultlog.logFault(__name__, source_faultlog.tagSearch, titles[0] + '&' + site)