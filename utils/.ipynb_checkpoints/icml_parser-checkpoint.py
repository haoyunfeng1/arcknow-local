import pymupdf
from pathlib import Path
from tqdm import tqdm
import pickle
import argparse

def parse_one_file(file_name):
    '''Parse single paper pdf file'''
    content = pymupdf.open(file_name)
    
    all_lines = []
    for page in content:
        p = page.get_text('dict')
        for b in p["blocks"]:
            if b["type"] == 0:
                for line in b["lines"]:
                    if line["spans"][0]["size"] > 7:
                        all_lines.append(line)
                        
    sections_start = False
    title = ''
    authors = []
    sections = []
    section = {}
    for line in all_lines:
        if not sections_start \
        and line['spans'][0]['font'] == 'NimbusRomNo9L-Medi' \
        and line['spans'][0]['size'] >= 11.5 \
        and line['spans'][0]['size'] <= 12.5 \
        and line['spans'][0]['text'].lower() == 'abstract':
            sections_start = True
                
        if not sections_start \
        and line['spans'][0]['font'] == 'NimbusRomNo9L-Medi' \
        and line['spans'][0]['size'] >= 14 \
        and line['spans'][0]['size'] <= 15:
            title_t = ' '.join([s["text"] for s in line["spans"]]).strip()
            if title:
                title += ' ' + title_t
            else: 
                title = title_t
            
        if not sections_start \
        and line['spans'][0]['font'] == 'NimbusRomNo9L-Medi' \
        and line['spans'][0]['size'] >= 9.5 \
        and line['spans'][0]['size'] <= 10.5:
            for s in line['spans']:
                if len(s['text']) > 0 and s['text'][0].isalpha():
                    authors.append(s['text'])

        if sections_start \
        and line['spans'][0]['font'] == 'NimbusRomNo9L-Medi' \
        and line['spans'][0]['size'] >= 11.5 \
        and line['spans'][0]['size'] <= 12.5:
            if section:
                sections.append(section)
            section = {'section_title': ' '.join([s['text'] for s in line['spans']]).strip(),
                       'section_content': ''}

        if sections_start \
        and line['spans'][0]['size'] >= 9.5 \
        and line['spans'][0]['size'] <= 10.5:
            section['section_content'] += ' '.join([s['text'] for s in line['spans']]).strip() + '\n'
        
        if sections_start \
        and line['spans'][0]['font'] == 'NimbusRomNo9L-Medi' \
        and line['spans'][0]['size'] >= 11.5 \
        and line['spans'][0]['size'] <= 12.5 \
        and line['spans'][0]['text'].lower() == 'references':
            break

    return {
        'title': title, 
        'authors': authors, 
        'sections': sections
    }

def parse_folder(folder_name):
    '''
    Parse all paper pdf files under folder folder_name.
    Store output in list of json [{'title': <title_str>, 'authors': <list of authors>, 'sections': <list of sections>}]
    '''
    folder_path = Path(folder_name)
    pdf_path = list(folder_path.glob('*.pdf'))
    all_papers = []
    for pdf in tqdm(pdf_path):
        paper = parse_one_file(pdf)
        all_papers.append(paper)
    return all_papers

def paper_json_to_text(paper_json):
    '''
    Convert paper from json format to text format 
    '''
    paper = paper_json['title'] + '\n\n'
    for section in paper_json['sections']:
        paper += section['section_title'] + '\n' + section['section_content'] + '\n\n'
    return paper

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parse papers')
    parser.add_argument('--project_dir', 
                        action="store", 
                        dest='project_dir', 
                        help='Directory to the project, should have papers folder with papers in pdf format', 
                        required=True)
    args = parser.parse_args()
    all_papers = parse_folder(Path(args.project_dir, 'papers'))
    with open(Path(args.project_dir, 'all_papers.pkl'), 'wb') as f:
        pickle.dump(all_papers, f)

#python utils/icml_parser.py --project_dir examples/icml_2024/


        