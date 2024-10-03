# formal_definition_grounding

We extract definitions from Wikipedia by the following steps:
1. Select a Wikipedia page which contain a definition of a mathematical object or concept.
2. Use its editing page to copy texts to txt files.
3. Use [Pandoc](https://pandoc.org/index.html) to convert txt files to latex files by the following command:
```
pandoc input.txt -f mediawiki -t latex --standalone -o output.tex
```
4. Extract relevant definition in LaTeX and do some modifications to add definition tag ``Definition of (name)'' and clean the text.

