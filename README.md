# LLM4UT

This is the artifact of our submission in ASE, including the prompt construction code and the evaluation code. 

⭐ We published a new project [UTGen_LLM](https://github.com/LeonYang95/UTGen_LLM) for more details about invoking the LLM to generate unit tests.

⭐**NOTE: The illustration examples of our research questions are listed in `running_example`.**

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
2. Download Junit 4, Mockito 5, powermock 2, hamcreset 2.1 and other necessary dependency jar file, and put it into `/path/to/defects4j/framework/projects/lib` to make sure that the unit tests can compile under junit4. In the futurem, we will publish a docker image that contains complete runtime environment.
3. Checkout **ALL** defects4j projects, including both fixed version and buggy version, roughly 1,600 checkouts. Please make sure the structure is `{Bug_id}/fixed` and `{Bug_id}/buggy` for the fixed version and buggy version respectively. 
The folder name tha contains all the projects of defects4j bugs is `d4j_proj_base`, which will be used later in configuration.
4. Please follow the `requirements.txt` file for python package installation.

## Execution 
1. Using the scripts in `rq1` folder (e.g., `generate_prompts.py`) to generate prompt for LLMs.
2. Using the genrated prompts and getting responses. This was done outside of the project, using an inference script, which simply feeds LLMs with the prompt and gathers the results. Please make sure the key in the json objects that holds the LLMs' responses is `completion`. Or you may need to change code accordingly.
   **Here we listed all prompt generation scripts used in our evaluation. All of our experiments after model inference are the same.**
3. Asking LLMs to response according to the prompts. Due to company policy, here we omitted our detailed results. We will release them after acceptance.
4. Create a directory under `data` to hold the generation results.
5. Please follow `configuration_example.py` to create your own configuration file, e.g., `configuration.py`.
6. Make sure you have the proper settings, and then, just run `rq1/rq1_starter.py`, the results will be saved according to your configuration.
7. Run scripts under `rq1/analyze` to obtain statistical analysis results.

## Details about `Configuration.py`
Here are the meanings of the settings in `configuration_example.py`

```python
d4j_home = "/path/to/defects4j"
d4j_proj_base = f"{d4j_home}/d4j_projects" # This is where you placed ALL defects4j projects
output_dir = 'data/rq1/results_1220' # Relative Path is fine. we will automatically insert the path to LLM4UT project.
python_bin = '/path/to/your/python/enivronment/bin/python' 
dej_command = f'{d4j_home}/framework/bin/defects4j'

projects = [...] # the defects4j projects that you wish to run
target_models = [...] # the models you wish to test, the results will be placed under the folder with the model names.

formats = [...] # comment for Code-Language-Description and natural for Natural-Language-Description. Details can be found in running_examples.

strategies = [...]

ablations = [...] # Controls which the code features you wish to use.
```








