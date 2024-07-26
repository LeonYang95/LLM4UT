# LLM4UT

This is the artifact of our submission in ASE, including the prompt construction code and the evaluation code.


## Structure
```
running_examples: Due to the page limit, we add some illustration examples in this repo.

rq1: Main code. Scripts of both prompt construction and evaluation are here

utils: Some utility methods.
```

## Environment

1. To fully run our evaluation, please first follow the setups from Defects4J benchmark, and make sure it works fine.
2. Checkout **ALL** defects4j projects, including both fixed version and buggy version. Please make sure the structure are `{Bug_id}/fixed` and `{Bug_id}/buggy` for the fixed version and buggy version respectively. 
The folder name tha contains all the projects of defects4j bugs is `d4j_project_base`, which will be used later in configuration.
3. Please follow the `requirements.txt` file for python package installation.
4. Use the prompt generation script
5. 






