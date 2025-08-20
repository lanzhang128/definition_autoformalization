# Formalizing Complex Mathematical Statements with LLMs: A Study on Mathematical Definitions
## File Description
**autoformalization.py** and **autoformalization_lean.py** are used for performing zero-shot autoformalization and refinement experiments in Isabelle/HOL and Lean4, respectively. **syn_test.py** and **syn_test_lean.py** are used for checking syntax errors for formal codes. The implementation of Lean4 theorem prover is from this repository: https://github.com/lanzhang128/multi_agent_autoformalization. **check_logs.py** is used for analysing error details for error categories. 

## More detailed steps for extracting definitions from Wikipedia
We extract definitions from Wikipedia by the following steps:
1. Select a Wikipedia page which contain a definition of a mathematical object or concept.
2. Use its editing page to copy texts to txt files.
3. Use [Pandoc](https://pandoc.org/index.html) to convert txt files to latex files by the following command:
```
pandoc input.txt -f mediawiki -t latex --standalone -o output.tex
```
4. Extract relevant definition in LaTeX and do some modifications to add definition tag "Definition of (name)" and clean the text.

## Data, Prompts & Results
We provide the datasets under **data** folder, prompts under **prompts** folder, and results in [Google Drive](https://drive.google.com/file/d/1NtIo2rwGxrl9Ao-JRSGKVPMvznetnByG/view?usp=sharing).

## Cite
If you find this repository useful, please cite:
```
@misc{zhang2025formalizingcomplexmathematicalstatements,
      title={Formalizing Complex Mathematical Statements with LLMs: A Study on Mathematical Definitions}, 
      author={Lan Zhang and Marco Valentino and Andre Freitas},
      year={2025},
      eprint={2502.12065},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2502.12065}, 
}
```
