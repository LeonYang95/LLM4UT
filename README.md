# LLM4UT

This is the artifact of our submission in ASE, including the prompt construction code and the evaluation code.


## Structure
```
LLM4UT
│
├── data // Contains data and configuration files
│
├── baselines // For evosuite only.
│
├── rq1 // Main code. Scripts of both prompt construction and evaluation are here
│
├──running_examples: // Due to the page limit, we add some illustration examples in this repo.
│
├──utils: Some utility methods.
```

## Setup

1. To fully run our evaluation, please first follow the setups from Defects4J benchmark, and make sure it works fine.
2. Checkout **ALL** defects4j projects, including both fixed version and buggy version. Please make sure the structure are `{Bug_id}/fixed` and `{Bug_id}/buggy` for the fixed version and buggy version respectively. 
The folder name tha contains all the projects of defects4j bugs is `d4j_project_base`, which will be used later in configuration.
3. Please follow the `requirements.txt` file for python package installation.

## Execution 
1. Using the scripts in `rq1` folder (e.g., `generate_prompts.py`) to generate prompt for LLMs.
2. Using the genrated prompts and getting responses. This was done outside of the project, using an inference script, which simply feeds LLMs with the prompt and gathers the results. Please make sure the key in the json objects that holds the LLMs' responses is `completion`. Or you may need to change code accordingly.
3. Create a directory under `data` to hold the generation results.
4. Please follow `configuration_example.py` to create your own configuration file, e.g., `configuration.py`.
5. Make sure you have the proper settings, and then, just run `rq1/rq1_starter.py`, the results will be saved according to your configuration.
6. Run scripts under `rq1/analyze` to obtain statistical analysis results.

## Details about `Configuration.py`








