# Getting to Philosophy

This project fetches a page from Wikipedia and follows the first link on that page until the [Wikipedia page for Philosophy](https://en.wikipedia.org/wiki/Philosophy) is reached.

The first link that matches the following criteria is always used:
* The link is an internal link to another Wikipedia page
* The link does not point to itself
* The link is not in italicized or parenthesized text
* The link is valid

The program will stop when one of the following conditions are met:
* The Philosophy page is found
* A loop of pages is found
* A maximum number of links to visit is exceeded
* A dead end is reached (there are no valid links on the page)

### Installation
pip install -r requirements.txt

### Usage
`python getting_to_philosophy.py [-m MAX_HOPS] [-l] STARTING_LINK`

positional arguments:
* STARTING LINK: The URL for a Wikipedia page to begin the search from

optional arguments:
* -m MAX_HOPS, --max_hops MAX_HOPS : Number of links to follow before quitting.
* -l, --ignore_loops  : Instead of terminating, choose the next link if a loop is found.

