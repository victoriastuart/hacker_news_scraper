# hacker_news_scraper

A Python 3 script for scraping the [Hacker News](https://news.ycombinator.com/news) feed, filtering that content by

* number of points, and/or
* number of comments, and/or
* excluding posts {dead | flagged | youtube | wikipedia | ...} according to a keywords list

Run via `~/.bashrc` alias or `crontab` (see notes near top of script).

Sample output: [hn.txt](https://github.com/victoriastuart/hacker_news_scraper/blob/master/hn.txt)

**Updates**

* I provided a script, [hn-regex_test.py](https://github.com/victoriastuart/hacker_news_scraper/blob/master/hn-regex_test.py) for testing regex expressions over "hn.txt" output file:

  * hn.txt output (raw, before postprocessing): [hn.2020.05.03.raw.txt]()
  * hn.txt output (after postprocessing): [hn.2020.05.03.postprocessed.txt]()

* added a dictionary and a method, `multiple_replace()`, to "hn.py" for postprocessing of various annoyances; e.g., the  BeautifulSoup "smart quotes" that get added to the "hn.txt" output file
