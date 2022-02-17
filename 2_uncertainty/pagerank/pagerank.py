import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    # here *************
    for corp in corpus:
        print(f"  {corp}:  \t{corpus[corp]}")
    tran = transition_model(corpus, list(corpus.keys())[2], DAMPING)
    print(tran)
    print()
    # here *************
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(ranks)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    # initializes prob with all pages
    prob = {page:0 for page in corpus}

    # if there is no link, random to each one and return
    if len(corpus[page]) == 0:
        for page in corpus:
            prob[page] = 1 / len(corpus)
        return prob

    # for all links, updates the probability with "damping_factor"
    for link in corpus[page]:
        prob[link] = damping_factor / len(corpus[page])
    
    # for all pages randomly, updates probability wih "1 - damping"
    for page in corpus:
        prob[page] += (1 - damping_factor) / len(corpus) 
    
    return prob


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # creates a counter and population
    pg_count = {page:0 for page in corpus}
    population = list(corpus.keys())

    # choose first page randomnly
    page = random.choices(population)[0]

    # Count all the times that the page is selected, of all n times
    for i in range(n):
        weights = list(transition_model(corpus, page, damping_factor).values())
        page = random.choices(population, weights=weights, k=1)[0]
        pg_count[page] += 1  

    sample = {page:pg_count[page]/n for page in pg_count}
    return sample 



def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    pg = {page:0 for page in corpus}

    return pg
    # raise NotImplementedError


if __name__ == "__main__":
    main()
