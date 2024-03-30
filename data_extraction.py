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

    # Construct your prompt carefully! Here's a basic example:
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

test_desc = """
There are many excellent resources across the Discord server, but Discord is optimized for ongoing conversation and useful knowledge and created materials are often lost. The official drive was sometimes hard to find, and several volunteers have their own collection of documents, notes, tips, strategies, lessons learned, etc. Many of these would be useful to other members.

Project specs for a central repo of knowledge and materials:
The folder structure should be maximally useful
Edit access is given on a per-folder or per-file basis as needed
It will be updated on a regular basis with new materials from across the Discord
Writers can be recruited to draft or edit documents directly in the centralized shared drive
The question "Where is [piece of info with ongoing usefulness]?" and "Where should this be stored for future reference?" should be easily answered with a drive link

I have been given access to manage this project on an ongoing basis. I have experience in shared file management and organization, I'm open to feedback, and I have a tendency to keep my eyes peeled for information that would be useful to others.

How You Can Help:
Tiny: Share existing files from your own collection that are relevant to PauseAI and that you think would be useful for other people to have (a copy can be added to the drive)
Tiny: Tag me when material shows up in the Discord stream that you believe should be added to the permanent knowledge base
Tiny: Give feedback about the Google Drive
Medium: Write definitive informational documents about various volunteer actions
"""
if __name__ == "__main__":
    result = extract_tasks_from_description(test_desc)
    print(result)