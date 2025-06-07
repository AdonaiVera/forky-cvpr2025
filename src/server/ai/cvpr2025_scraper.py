import requests
from bs4 import BeautifulSoup
import json
import re
from tqdm import tqdm

def fetch_openaccess_papers():
    url = 'https://openaccess.thecvf.com/CVPR2025?day=all'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    papers = {}
    
    # Get total number of papers for progress bar
    total_papers = len(soup.find_all('dt'))
    
    for dt in tqdm(soup.find_all('dt'), desc="Fetching papers", total=total_papers):
        title_tag = dt.find('a')
        if title_tag:
            title = title_tag.text.strip()
            paper_url = 'https://openaccess.thecvf.com' + title_tag['href']
            dd = dt.find_next_sibling('dd')
            link_tags = dd.find_all('a')
            authors = []
            for a in link_tags:
                href = a.get('href', '')
                # Handle authors (they link to '#')
                if href == '#': 
                    authors.append(a.text.strip())
    
            # Fetch abstract from paper page
            paper_response = requests.get(paper_url)
            paper_soup = BeautifulSoup(paper_response.text, 'html.parser')
            abstract_tag = paper_soup.find('div', id='abstract')
            abstract = abstract_tag.text.strip() if abstract_tag else ''

            # Find links in the detail page
            detail_links = paper_soup.find_all('a')
            links = {}

            for a in detail_links:
                text = a.text.strip()
                href = a.get('href', '')
                if text in ['pdf', 'supp', 'arXiv']:
                    links[text.strip('[]').lower()] = 'https://openaccess.thecvf.com' + href

            papers[title] = {
                'title': title,
                'authors': authors,
                'pdf': links.get('pdf'),
                'supp': links.get('supp'),
                'arxiv': links.get('arXiv'),
                'bibtex': links.get('bibtex'),
                'abstract': abstract
            }
            
    return papers

def fetch_poster_info():
    url = 'https://cvpr.thecvf.com/Conferences/2025/AcceptedPapers'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    posters = {}
    rows = soup.find_all('tr')
    
    # Get total number of rows for progress bar
    total_rows = len(rows)
    
    for row in tqdm(rows, desc="Processing poster info", total=total_rows):
        cells = row.find_all('td')
        if len(cells) < 2:
            continue

        left_cell = cells[0]
        right_cell = cells[-1]

        

        # Extract title
        title_tag = left_cell.find(['strong', 'a'])
        if not title_tag:
            continue

        title = title_tag.text.strip()

        # Extract poster session info (in left cell)
        session_match = re.search(r'Poster Session \d+', left_cell.get_text())
        poster_session = session_match.group() if session_match else ''

        # Extract location (in right cell)
        poster_location = right_cell.get_text(strip=True).replace('\xa0', ' ')
        poster_location = ' '.join(right_cell.get_text(separator=' ', strip=True).split())

        posters[title] = {
            'poster_session': poster_session,
            'poster_location': poster_location
        }

        print(f"title: {title}")

    return posters

def merge_data(papers, posters):
    for title in tqdm(papers, desc="Merging data"):
        if title in posters:
            papers[title].update(posters[title])
        else:
            papers[title].update({'poster_location': '', 'poster_session': ''})
    return papers

def main():
    papers = fetch_openaccess_papers()
    posters = fetch_poster_info()
    merged_data = merge_data(papers, posters)
    with open('cvpr2025_papers.json', 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    main()
