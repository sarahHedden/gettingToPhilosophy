from bs4 import BeautifulSoup
import argparse
import requests
import sys
import urllib

"""
Finds the first link on a Wikipedia page in the main body excluding
italicized and parenthesized links.
params:
    url(str): link to a wikipedia page.
    ignore_loops(bool): skip loops instead of stopping when a loop is found.
    visited(dict): list of already visited links.  Only used if
        ignore_loops is set to True.
returns: url of the first link, or None if a valid link is not found.
"""
def find_first_link(url: str, ignore_loops: bool, visited: dict) -> str:
    response = requests.get(url)
    if not response.ok:
        print(url, "could not be reached")
        return None
    
    soup = BeautifulSoup(response.content, "html.parser")
    
    # get main body
    content = soup.find(id="mw-content-text").find(class_="mw-parser-output")

    # remove tables and italicized elements
    for item in content.find_all("table") + content.find_all("i"):
        item.decompose()
        
    paragraphs = content.find_all("p", recursive=False)
    for paragraph in paragraphs:
        links = paragraph.find_all("a")
        text = paragraph.text
        for link in links:
            if 'href' in link.attrs and "/wiki" in link['href'] \
                and ":" not in link['href']:
                index = text.find(link.text)
                text_before = text[:index]

                if text_before.count("(") > text_before.count(")"):
                    # do not include parenthesized links
                    continue
                
                next_link = urllib.parse.urljoin(
                    'https://en.wikipedia.org/', link['href'])
                if ignore_loops and next_link in visited:
                    continue
                if next_link == url:
                    continue
                return next_link
    return None

"""
Follow the first links on a wikipedia page until the goal url, a loop,
or a dead end is found.
params:
    url(str): the url to start at.
    goal(str): the url to stop at.
    max_hops(int): the number of links to follow before abandoning the search.
    ignore_loops(bool): skip loops instead of stopping when a loop is found.
returns: list of urls visited to reach the goal in order.  An empty list will
    be returned if there is no valid path.
"""
def search_first_links(url: str = "https://en.wikipedia.org/wiki/Special:Random",
                       goal: str = "https://en.wikipedia.org/wiki/Philosophy",
                       max_hops: int = 100,
                       ignore_loops: bool = False) -> list:
    visited = {url: True}
    path = [url]
    current_url = url
    hops = 0
    print(url)

    while hops < max_hops and current_url != goal:
        next_url = find_first_link(current_url, ignore_loops, visited)
        if next_url is None:
            print("NO VALID LINKS!")
            return []

        if next_url in visited:
            print("LOOP FROM", next_url)
            return []
                  
        print(next_url)
        path.append(next_url)
        visited[next_url] = True
        current_url = next_url
        hops += 1

    if hops >= max_hops:
        print("MAX HOPS EXCEEDED")
        return []
    return path
    
def main():
    parser = argparse.ArgumentParser(
        description="Follow wikipedia links to find the Philosophy page.")
    parser.add_argument("url", type=str, help="URL to begin searching from.")
    parser.add_argument("-m", "--max_hops", default=100, type=int,
                        action="store",
                        help="Number of links to follow before quitting.")
    parser.add_argument("-l", "--ignore_loops", action="store_true",
                        help="Choose the next link if a loop is found.")
    args = parser.parse_args()
    path = search_first_links(args.url, max_hops=args.max_hops,
                              ignore_loops=args.ignore_loops)
    if len(path) > 0:
        print(len(path)-1, "hops")
    else:
        print("Path not found")

if __name__ == "__main__":
    main()
    
    
    
