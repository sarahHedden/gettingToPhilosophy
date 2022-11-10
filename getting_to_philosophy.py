import argparse
import urllib
import requests
from bs4 import BeautifulSoup

def find_first_link(url: str, content: bytes, ignore_loops: bool, visited: dict) -> str:
    """
    Finds the first link on a Wikipedia page in the main body excluding
    italicized and parenthesized links.
    params:
        url(str): link to a wikipedia page.
        content(bytes): content on the page for the given url.
        ignore_loops(bool): skip loops instead of stopping when a loop is found.
        visited(dict): list of already visited links.  Only used if
            ignore_loops is set to True.
    returns:
        next_link(str): url of the first link, or None if a valid link is not found.
        content(bytes): content of the next url webpage.
    """
    soup = BeautifulSoup(content, "html.parser")
    body = soup.find(id="mw-content-text").find(class_="mw-parser-output")

    # remove tables and italicized elements
    for item in body.find_all("table") + body.find_all("i"):
        item.decompose()

    paragraphs = body.find_all("p", recursive=False)
    for paragraph in paragraphs:
        links = paragraph.find_all("a")
        for link in links:
            if ('href' in link.attrs and "/wiki" in link['href']
                and ":" not in link['href']):
                link_index = paragraph.text.find(link.text)
                text_before = paragraph.text[:link_index]

                if text_before.count("(") > text_before.count(")"):
                    # do not include parenthesized links
                    continue

                next_link = urllib.parse.urljoin(
                    'https://en.wikipedia.org/', link['href'])
                if ignore_loops and next_link in visited:
                    continue
                if next_link == url:
                    continue

                response = requests.get(next_link)
                if response.ok:
                    return next_link, response.content
    return None, None

def search_first_links(url: str = "https://en.wikipedia.org/wiki/Special:Random",
                       goal: str = "https://en.wikipedia.org/wiki/Philosophy",
                       max_hops: int = 100,
                       ignore_loops: bool = False) -> list:
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
    visited = {url: True}
    path = [url]
    current_url = url
    hops = 0

    response = requests.get(url)
    if not response.ok:
        print("Could not access", url)
        return []
    page_content = response.content
    print(url)

    while hops < max_hops and current_url != goal:
        next_url, page_content = find_first_link(current_url, page_content,
                                                 ignore_loops, visited)
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
