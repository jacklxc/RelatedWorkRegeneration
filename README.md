# RelatedWorkRegeneration
This repository includes the source code for the COLING 2025 paper [Explaining Relationships Among Research Papers](https://arxiv.org/pdf/2402.13426).

## Steps to replicate the experiments
* Fill out `google_search_example.sh` to Google search the paper PDF given paper title or link.
* Run [doc2json](https://github.com/allenai/s2orc-doc2json) to parse PDFs into JSON format.
* Run `example_related_work_generation_full.ipynb` to re-generate the related work section of the given paper. The `joint_tagger.py` module is derived from [CORWA](https://github.com/jacklxc/CORWA).

Note that this paper and experiment is exploratory and not intended to deliver any usable products due to ethical and other technical issues. Please refer to our paper for details.