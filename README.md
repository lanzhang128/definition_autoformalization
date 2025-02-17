# Formalizing Complex Mathematical Statements with LLMs: A Study on Mathematical Definitions

## More detailed steps for extracting definitions from Wikipedia
We extract definitions from Wikipedia by the following steps:
1. Select a Wikipedia page which contain a definition of a mathematical object or concept.
2. Use its editing page to copy texts to txt files.
3. Use [Pandoc](https://pandoc.org/index.html) to convert txt files to latex files by the following command:
```
pandoc input.txt -f mediawiki -t latex --standalone -o output.tex
```
4. Extract relevant definition in LaTeX and do some modifications to add definition tag ``Definition of (name)'' and clean the text.

## Results
We provide our results in Google Drive: [miniF2F](https://drive.google.com/file/d/1yQdzuF07vsZOVlPj_rslCOuDkPMYIEDH/view?usp=drive_link), [Def_Wiki](https://drive.google.com/file/d/1hGJCVuD4zPEO9VMzCWIDGqziSLxQvBRM/view?usp=drive_link),  [Def_ArXiv](https://drive.google.com/file/d/1co858qls77E3yZHzN4GMJfv4sr2v_GHT/view?usp=sharing).
