from openai import OpenAI
import requests

"""
The following code fetches lineage information from UniProt (using a tool binded to an LLM) to get Pathogen class 
(Virus, Fungus, Helminth, Bacteria, Prion, or Protozoa).
"""



# Initialize the OpenAI client

url = "http://lambda5.cels.anl.gov:44497/v1"
client = OpenAI(
    base_url=url,
    api_key="."
)

# Define the tool function
def get_InfectiousAgentClass(pathogen_name: str):
    """
    Fetches pathogen lineage from UniProt.

    Args:
        pathogen_name (str): The name of the pathogen (e.g., "mpox").

    Returns:
        list: Lineage of the pathogen.
    """
    query = pathogen_name.replace(" ", "+")
    url = f"https://rest.uniprot.org/taxonomy/search?query={query}&format=json"
    response = requests.get(url).json()
    lineage = response["results"][0].get("lineage", [])
    return lineage


def get_pathogen_class(pathogen_name: str):
    # Define the system and user messages
    messages = [
        {
            "role": "system",
            "content": """You are a biomedical AI assistant. 
    You are given a pathogen name and can use the available tool to infer its type.
    Respond with one of the following only:
    Virus, Fungus, Helminth, Bacteria, Prion, or Protozoa."""
        },
        {"role": "user", "content": pathogen_name}
    ]


    # Define the tool schema for the model to call
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_InfectiousAgentClass",
                "description": "Fetches pathogen lineage from UniProt.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pathogen_name": {
                            "type": "string",
                            "description": "The name of the pathogen (e.g., 'mpox')."
                        }
                    },
                    "required": ["pathogen_name"]
                }
            }
        }
    ]


    # Step 1: Model decides whether to call the tool
    response = client.chat.completions.create(
        model="gpt-4.1",  # You can replace with gpt-4o, gpt-4.1-mini, etc.
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )

    tool_call = response.choices[0].message.tool_calls

    if tool_call:
        # The model requested a tool call
        func_name = tool_call[0].function.name
        func_args = eval(tool_call[0].function.arguments)
        result = get_InfectiousAgentClass(**func_args)

        # Step 2: Send the tool result back to the model
        messages.append(response.choices[0].message)
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call[0].id,
            "name": func_name,
            "content": str(result)
        })

        final_response = client.chat.completions.create(
            model="gpt-4.1",
            messages=messages
        )
        print("Lineage was retrieved from UniProt. LLM used the available tool.")
        return final_response.choices[0].message.content
    else:
        # Model responded directly
        return response.choices[0].message.content 
