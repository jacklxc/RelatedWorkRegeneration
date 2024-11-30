import argparse
import os
import json
import requests
from googlesearch import search
from bs4 import BeautifulSoup
from time import sleep
from tqdm import tqdm
from glob import glob
from prompting_util import is_related_work_section

def scrape_and_download_url(URL):
    global visited_urls
    global failed_urls
    try:
        r = requests.get(URL)
        soup = BeautifulSoup(r.content, 'html5lib')

        download_pdf = True
        if URL[-4:] == ".pdf":
            pdf_url = URL
            pdf_file_name = os.path.split(URL)[-1]

        elif "aclanthology.org/" in URL:
            if ".pdf" not in URL:
                if URL[-1] == "/":
                    pdf_url = URL[:-1]+".pdf"
                else:
                    pdf_url = URL+".pdf"
            else:
                pdf_url = URL
            pdf_file_name = os.path.split(pdf_url)[-1]

        elif "arxiv.org/abs/" in URL:
            arxiv_id = os.path.split(URL)[-1]
            pdf_url = "https://arxiv.org/pdf/"+arxiv_id+".pdf"
            pdf_file_name = arxiv_id + ".pdf"

        elif "link.springer.com/article/" in URL:
            pdf_url = soup.find('meta',attrs = {'name':'citation_pdf_url'}).attrs["content"]
            pdf_file_name = os.path.split(pdf_url)[-1] + ".pdf"

        elif "ceur-ws.org" in URL and ".pdf" in URL:
            pdf_url = URL
            pdf_file_name = os.path.split(URL)[-1]

        elif "ncbi.nlm.nih.gov/pmc/articles/" in URL:
            pdf_url = URL
            download_pdf = False

        elif "onlinelibrary.wiley.com/doi/abs/" in URL: # Not open access
            pdf_url = URL
            download_pdf = False

        elif "sciencedirect.com/science/article/" in URL: # sciencedirect does not like bots!
            paper_id = os.path.split(URL)[-1]
            pdf_file_name = paper_id+".pdf"
            pdf_url = "https://www.sciencedirect.com/science/article/pii/" + paper_id + "/pdfft?isDTMRedir=true&download=true"
            download_pdf = False

        else:
            pdf_url = URL
            filename = os.path.split(URL)[-1]
            if filename[-4:] != ".pdf":
                pdf_file_name = filename + ".pdf"
            else:
                pdf_file_name = filename

        if pdf_url in visited_urls:
            print("Already visited pdf_url.")
        else:
            r = requests.get(pdf_url)
            content_type = r.headers.get('content-type')
            visited_urls.add(URL)
            visited_urls.add(pdf_url)
            if 'application/pdf' in content_type:
                with open(args.prefix+"/"+pdf_file_name, 'wb') as f:
                    f.write(r.content)
                #print("Downloaded PDF")
                #print(title, first_author_last_name, year)
                #print()
                return pdf_file_name
            else:
                #print("Failed downloading:", URL)
                failed_urls.append(URL)
                return None
    except:
        failed_urls.append(URL)
        return None

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--prefix', type=str)
    argparser.add_argument('--seed_query', type=str)
    argparser.add_argument('--seed_paper_name', type=str)
    argparser.add_argument('--related_work_keyword', nargs='+')
    argparser.add_argument('--keyword_relation', type=str, default="in")
    args = argparser.parse_args()
    
    visited_urls = set([])
    failed_urls = []
    search_results = {}
    
    #print(args.prefix)
    #print(args.seed_query)
    #print(args.related_work_keyword)
    #print(args.keyword_relation)
    
    if args.seed_query is not None:
        if not os.path.exists(args.prefix):
            os.mkdir(args.prefix)
        if args.seed_query[-4:]!=".pdf":
            result = search(args.seed_query, num_results=1)
            urls = [url for url in result]
            search_results[args.seed_query] = urls
            pdf_file_name = scrape_and_download_url(search_results[args.seed_query][0])
        else:
            pdf_file_name = scrape_and_download_url(args.seed_query)
        print("End initial query.","Seed file name:",pdf_file_name)
    elif args.prefix is not None:
        available_jsons = glob(args.prefix+"/*.json")
        if len(available_jsons) == 1 or args.seed_paper_name is not None:
            if args.seed_paper_name is None:
                initial_json_name = glob(args.prefix+"/*.json")[0]
            else:
                initial_json_name = args.prefix+"/"+args.seed_paper_name.replace(".pdf",".json")
            
            with open(initial_json_name) as f:
                target_json = json.load(f)
            print("Seed paper:", target_json["title"])
            cited_titles = set([])
            section_titles = []
            for paragraph in target_json["pdf_parse"]["body_text"]:
                if paragraph["section"] not in section_titles:
                    section_titles.append(paragraph["section"])
                if is_related_work_section([kw.lower() for kw in args.related_work_keyword], paragraph["section"].lower(), args.keyword_relation):
                    for span in paragraph["cite_spans"]:
                        if span["ref_id"]:
                            cited_titles.add(target_json["pdf_parse"]["bib_entries"][span["ref_id"]]["title"])
            print(section_titles)
            print("Cited titles:")
            print(cited_titles)
            
            for query in tqdm(cited_titles):
                sleep(1)
                result = search(query, num_results=1)
                urls = [url for url in result]
                search_results[query] = urls
            print("Finished Google search. Downloading PDFs:")
            for title in tqdm(cited_titles):
                urls = search_results[title]
                URLs = [urls[0]]
                for URL in URLs:
                    #print(URL)
                    if URL in visited_urls:
                        print("Already visited URL",URL)
                        continue
                    pdf_file_name = scrape_and_download_url(URL)
                    sleep(1)    
            print("Finished downloading.")
            if len(failed_urls) > 0:
                print("Failed URLs:")
                print(failed_urls)
                
        elif len(available_jsons)==0:
            print("No Json found. Terminated.")
        else:
            print("Too many Jsons found. Terminated.")
    else:
        print("Error Googling! Terminated.")