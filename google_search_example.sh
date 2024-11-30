prefix="example_pdfs"
seed_query="https://aclanthology.org/2022.naacl-main.XXX.pdf"
related_work_keyword=("automatic related work generation")
keyword_relation="in"
python google_search_papers.py --prefix $prefix --seed_query "$seed_query" --related_work_keyword "${related_work_keyword[@]}" --keyword_relation $keyword_relation
source convert_folder.sh $prefix
python google_search_papers.py --prefix $prefix --related_work_keyword "${related_work_keyword[@]}" --keyword_relation $keyword_relation
source convert_folder.sh $prefix