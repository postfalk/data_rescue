import os
import re
import requests
from selenium.webdriver import Firefox # pip install selenium


PATTERNS=[r'http:\/\/.*\.pdf', r'http:\/\/.*\.7z', r'\/\/.*\.zip']
# START_URL = 'http://www.horizon-systems.com/NHDPlus/NHDPlusV2_18.php'
# START_URL = 'https://coast.noaa.gov/slrdata/'
# DESTINATION_FOLDER = '/Volumes/feddata/slrdata/'
START_URL = 'https://walrus.wr.usgs.gov/coastal_processes/cosmos/socal1.0/index.html'
DESTINATION_FOLDER = '../'


def ensure_folder(path):
    try:
       os.makedirs(path)
    except OSError:
        pass
    return

def fixurl(url):
    if not re.search(r'^http|https:', url) and re.search(r'^\/\/', url):
        url = 'http:{}'.format(url)
    return url


# see http://stackoverflow.com/questions/16694907/
# how-to-download-large-file-in-python-with-requests-py
def download_file(url):
    local_filename = os.path.join(DESTINATION_FOLDER, url.split('/')[-1])
    if not os.path.isfile(local_filename):
        url = fixurl(url)
        print 'Download {} to {}'.format(url, local_filename)
        r = requests.get(url)
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
                    f.flush()
    else:
        print 'File {} already exists.'.format(local_filename)
    return


def run_website(url):
    """Generate dynamic content with Selenium."""
    # use Firefox to get page with JavaScript generated content
    browser = Firefox()
    browser.get(url)
    ret = browser.page_source
    browser.close()
    return ret

def scrape_website(url, patterns):
    ret = []
    restext = run_website(url)
    for pattern in patterns:
        m = re.finditer(pattern, restext)
        for item in m:
            ret.append(item.group(0))
    return ret


def main():
    print 'Harvest all files linked in page by pattern'
    ensure_folder(DESTINATION_FOLDER)
    url_list = scrape_website(START_URL, PATTERNS)
    for url in url_list:
        download_file(url)


if __name__ == '__main__':
    main()
