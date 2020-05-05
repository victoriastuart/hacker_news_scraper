# hacker_news_scraper

A Python 3 script for scraping the [Hacker News](https://news.ycombinator.com/news) feed, filtering that content by

* number of points, and/or
* number of comments, and/or
* excluding posts {dead | flagged | youtube | wikipedia | ...} according to a keywords list

Run via `~/.bashrc` alias or `crontab` (see notes near top of script).

Sample output: [hn.txt](https://github.com/victoriastuart/hacker_news_scraper/blob/master/hn.txt)

**Updates**

* provided a script, [hn-regex_test.py]() for testing regex expressions over "hn.txt" output file

* added a dictionary and a method ("multiple_replace()") to "hn.py" for postprocessing of various annoyances (e.g. BeautifulSoup "smart quotes" that output to the "hn.txt" output file
