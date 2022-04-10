# NLP-Modern-Neural-Networks-Meet-Linguistic-Theory
This is the group project for the course Natural Language Processing. 


## Description

This repository has two main folders: ```datasets``` and ```experiments```.  


* The ```datasets``` folder contains code for creating German, Dutch and English corpus.
* The ```experiments``` folder contains the experiment code, parameter.yaml file and replicable output.

### 1. Preparing the datasets
You can prepare all datasets by running ```sh ./createALLdatasets.sh``` from within the folder ```datasets```. For English, German and Dutch a list of lemma's with wordforms is saved to ```[english|dutch|german]_bylemma_[orth|phon].txt```<p>
  After that, 6100 wordforms are saved to ```[src|tgt]_[train|test|valid].txt```
  
### 2. Running the experiments
You can run the experiments by starting ```jupyter lab experiment.ipynb``` from the ```experiments``` folder.
