# taboo-mon -- A Taboo library for parsing the Monsanto data into taboo parse-trees 

This is helper code for extracting the Monsanto dataset and parse it up as a series of sentence trees. The trees can be used with [taboo-core](https://github.com/neerbek/taboo-core) (see also this repository for dependencies) which can train and run neural networks for identifying sensitive information. 

See also: 

Jan Neerbek and Ira Assent and Peter Dolog  
Detecting Complex Sensitive Information via Phrase Structure in Recursive Neural Networks  
PAKDD '18  
https://doi.org/10.1007/978-3-319-93040-4_30  

To clone:

```
git clone https://github.com/neerbek/taboo-mon.git
```

## Notes:

python3 (obviously)

Dependencies: taboo-core, see [https://github.com/neerbek/taboo-core.git]

You should add taboo-core to PYTHON-PATH environment variable.

```
export PYTHONPATH=${PYTHONPATH}${PYTHONPATH:+:}<PATH-TO-TABOO-CORE>
```
ex
```
export PYTHONPATH=${PYTHONPATH}${PYTHONPATH:+:}$HOME/taboo-core
```

## Testing installation
To run tests: from taboo-mon, say:

```
./run_tests.sh
```

## Parsing data

### Download

```
# get list of links
wget -O index.html http://baumhedlundlaw.com/pdf/monsanto-documents/

# remove html tags
xmllint --html --xpath //a/@href index.html | sed 's/ href="\([^"]*\)"/\1\n/g' > links.txt
grep -v "?C=N;O=D$" links.txt | grep -v ";O=A$" | grep -v "^/pdf/$" > links2.txt
grep "/$" links2.txt && echo "have further directories"

# data directory
mkdir data_monsanto
mkdir data_monsanto/raw

# download all links
python3 download.py --inputfile=links2.txt --outdir=data_monsanto/data --baseurl="http://baumhedlundlaw.com/pdf/monsanto-documents/"

# zip file
wget -O data_monsanto/raw/monsanto-papers-zip-file.zip http://baumhedlundlaw.com/pdf/monsanto-documents/monsanto-papers-zip-file.zip

# subdir
wget -O daubert-brief.html http://baumhedlundlaw.com/pdf/monsanto-documents/daubert-brief
xmllint --html --xpath //a/@href daubert-brief.html | sed 's/ href="\([^"]*\)"/\1\n/g' > daubert-brief-links.txt
grep -v "?C=N;O=D$" daubert-brief-links.txt | grep -v ";O=A$" | grep -v "^/pdf/monsanto-documents/$" > daubert-brief-links2.txt
grep "/$" daubert-brief-links2.txt && echo "have further directories"

mkdir data_monsanto/raw/daubert-brief
python3 download.py --inputfile=daubert-brief-links2.txt --outdir=data_monsanto/raw/daubert-brief --baseurl="http://baumhedlundlaw.com/pdf/monsanto-documents/daubert-brief/"

# I got 2018-03-29
# 262 docs
# 1 zip file
# 125 docs

# rm tmp files
rm daubert-brief-links.txt daubert-brief-links2.txt daubert-brief.html index.html links.txt links2.txt 
```

### Parsing

```
# change the uri in monsantoLabelentries.py to data_monsanto/raw/monsanto-documents-chart-100917.pdf (or if newer exists)
# this is the labels by the lawers

# generates monsantoLabelEntries.json a json list of MonsantoDocuments.
python3 monsantoLabelEntries.py

# set variables datadir, decryptdir and filename inside the script textExtractor.py
# unlock encryption on pdfs and extract all text into *.txt files.
# Fixes some errors/inconsistencies in the original format.
python3 textExtractor.py

# We now have raw text and labels per document - to split into sentences and get parse-trees we do
python3 sentenceSpliter.py -o monexp-2018-04-17-15-58-01_trees.txt

# we can now use taboo-core to train on these trees
```
