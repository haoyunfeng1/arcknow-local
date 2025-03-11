import requests
from bs4 import BeautifulSoup
import urllib.request
from pathlib import Path
import argparse
from tqdm import tqdm
import socket

socket.setdefaulttimeout(100)

def download_papers(url, output_path):
    '''Download all the pdf links from <url> and store in <output_path>'''
    response = requests.get(url)
    # Check if the request was successful
    if response.status_code == 200:
        Path(output_path).mkdir(parents=True, exist_ok=True)
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')

        index = 0
        # Extract data from the HTML (example: extracting all links)
        links = soup.find_all('a')
        for link in tqdm(links):
            if link.get('href')[-4:] == '.pdf':
                paper_pdf = link.get('href')
                file_name = Path(output_path, f'paper_{index}.pdf')
                urllib.request.urlretrieve(paper_pdf, file_name)
                index += 1
    else:
        raise Exception(f"Request failed with status code {response.status_code}")
        
    return 0 

def download_nips(url, output_path):
    '''
    Download all the pdf links from <url> and store in <output_path>
    This handles NIPS proceedings page specifically https://papers.nips.cc/paper_files/paper/2024
    '''
    response = requests.get(url)
    if response.status_code == 200:
        Path(output_path).mkdir(parents=True, exist_ok=True)
        soup = BeautifulSoup(response.content, 'html.parser')
        links = soup.find_all('a')
        index = 0
        for link in tqdm(links):
            try:
                if link.get('href')[-24:] == 'Abstract-Conference.html':
                    r = requests.get('https://papers.nips.cc' + link.get('href'))
                    if r.status_code == 200:
                        soup = BeautifulSoup(r.content, 'html.parser')
                        ls = soup.find_all('a')
                        retrieved = False
                        for l in ls:
                            if l.get('href')[-4:] == '.pdf':
                                paper_pdf = l.get('href')
                                file_name = Path(output_path, f'paper_{index}.pdf')
                                urllib.request.urlretrieve('https://papers.nips.cc'+paper_pdf, file_name)
                                index += 1
                                retrieved = True
                        if not retrieved:
                            print("Cannot retrieve " + str(link))
                    else:
                        raise Exception(f"Request failed with status code {r.status_code}")
            except:
                print("Failed to retrieve " + str(link))
    else:
        raise Exception(f"Request failed with status code {response.status_code}")
    return 0

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download papers in pdf')
    parser.add_argument('--url', action="store", dest='url', help='url to the webpage with pdf links', required=True)
    parser.add_argument('--project_dir', action="store", dest='project_dir', help='project directory', required=True)
    args = parser.parse_args()
    output_path = Path(args.project_dir, 'papers').mkdir(parents=True, exist_ok=True)
    download_papers(args.url, output_path)

#python utils/download_pdfs_from_url.py --url "https://proceedings.mlr.press/v235/" --project_dir examples/icml_2024/