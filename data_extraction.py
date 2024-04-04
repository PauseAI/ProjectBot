from openai import OpenAI
import json
import jsonschema
import config

client = OpenAI(api_key = config.openai_api_key, organization=config.openai_organization)

def retries(f):
    """
    Allows to retry multiple times until we get an extraction that worked
    """
    def inner(*args, n_retries=3, **kwargs):
        for i in range(n_retries):
            result = f(*args, **kwargs)
            if result:
                return result
            print(f"retry {i}")
    return inner

@retries
def extract_tasks_from_description(project_description):
    """Sends a prompt to ChatGPT to extract list of tasks from the 
       project description.

    Args:
        project_description (str): The description of the project.

    Returns:
        list: A list of dictionaries. Each element corresponds to a task.
    """

    expected_schema = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "task": {"type": "string"},
                "involvement": {
                    "type": "string",
                    "enum": ["Tiny", "Small", "Medium", "Big"]  # Enforce valid values
                },
                "skills": {"type": "array", "items": {"type": "string"}} 
            },
            "required": ["task", "involvement", "skills"] 
        }
    }

    prompt = """You are a project assistant. You will be provided with a project description.
    Please provide a JSON response containing a list of elements representing each task in the project.
    Each list element is contains the following keys:
    * task: (String) One or two lines naming and describing the task
    * involvement: (String) Takes values in {"Tiny", "Small", "Medium", "Big"}
    * skills: (List of Strings) list all strings listed in the task description, if any

    Example:
    If the project description contains the following text

    How you can help
        Medium: Discuss this overall strategy, give feedback and suggest the groups that should be created. Skills: think write
        Big: Lead an Interest Group!

    Return the following json:
    [
        {
            "task": "Discuss this overall strategy, give feedback and suggest the groups that should be created.",
            "involvement": "Medium",
            "skills": ["think", "write"]
        },
        {
            "task": "Lead an Interest Group!",
            "involvement": "Big",
            "skills": []
        }
    ]

    This is important: your response should only contain the JSON object, nothing else.
    
    Here is the project description:
    """ + project_description

    response = client.chat.completions.create(
        model="gpt-3.5-turbo", # Or another suitable model
        messages=[{
            "role": "system",
            "content": prompt
        }]
    )

    extracted_data_json = response.choices[0].message.content.strip()

    try:
        extracted_data = json.loads(extracted_data_json)  # Load as JSON
        jsonschema.validate(instance=extracted_data, schema=expected_schema)
        return extracted_data  # Return a Python dictionary
    except (json.JSONDecodeError, jsonschema.ValidationError) as e:
        print(f"Error decoding JSON: {e}")
        return None  # Indicate failure
