from openai import OpenAI
import chainlit as cl
from sparql_llm.validate_sparql import extract_sparql_queries
from sparql_llm.utils import query_sparql
import json
from pathlib import Path

PATHOGEN_SCHEMA_FILE = Path("data", "Pathogen_schemav2.json")
EXAMPLE_FILE = Path("data", "sparql-examples.json")


with PATHOGEN_SCHEMA_FILE.open("r", encoding="utf-8") as f:
    schema_info = json.dumps(json.load(f), indent=2)
with EXAMPLE_FILE.open("r", encoding="utf-8") as f:
    example_queries = json.dumps(json.load(f), indent=2)


RAG_PROMPT = f"""
You are an assistant that helps users formulate SPARQL queries to be executed on a SPARQL endpoint.
Your role is to transform the user question into a SPARQL query based on the context provided in the prompt.

Your response must follow these rules:
    - Always output one SPARQL query.
    - Enclose the SPARQL query in a single markdown code block using the "sparql" language tag.
    - Include a comment at the beginning of the query that specifies the target endpoint using the following format: "#+ endpoint: ".
    - Use full URIs for all entities in the SPARQL query.
    - Prefer a single endpoint; use a federated SPARQL query only if access across multiple endpoints is required.
    - Do not add more codeblocks than necessary.
    
Here is a list of reference user questions and corresponding SPARQL query answers that will help you formulate the SPARQL query:

{example_queries}

If the information provided in the examples above is not sufficient to answer the question, you can advise the schema information below to help you formulate the SPARQL query.

{schema_info}
"""

url = "http://lambda5.cels.anl.gov:44497/v1"
# url = "https://argo-bridge.cels.anl.gov"

# Initialize the client with custom base URL and API key
client = OpenAI(
    base_url=url,
    api_key="."
)

def execute_query(last_msg: str) -> list[dict[str, str]]:
    """Extract SPARQL query from markdown and execute it."""
    for extracted_query in extract_sparql_queries(last_msg):
        if extracted_query.get("query") and extracted_query.get("endpoint_url"):
            res = query_sparql(extracted_query.get("query"), extracted_query.get("endpoint_url"))
            return res.get("results", {}).get("bindings", [])

@cl.on_message
async def on_message(msg: cl.Message):
    """Main function to handle when user send a message to the assistant."""
    
    messages = [
        {"role": "system", "content": RAG_PROMPT},
        {"role": "user", "content": msg.content},
        *cl.chat_context.to_openai(),
    ]


    max_try_count = 3
    query_success = False
    for _ in range(max_try_count):
        answer = cl.Message(content="")

        response = client.chat.completions.create(
            model="gpt5",
            messages=messages,
            stream=True,
            temperature=0.0,
            seed=42,
        )

        for r in response:
            delta = r.choices[0].delta
            if hasattr(delta, "content") and delta.content:
                await answer.stream_token(delta.content)
        await answer.send()


        if query_success:
            break

        query_res = execute_query(answer.content)
        if len(query_res) < 1:
            print("⚠️ No results, trying to fix")
            messages = [
                {"role": "user", "content": f"""The query you provided returned no results, please fix the query:\n\n{answer.content}"""},
                *cl.chat_context.to_openai(),
            ]
        else:
            print(f"✅ Got {len(query_res)} results! Summarizing them, then stopping the chat")
            async with cl.Step(name=f"{len(query_res)} query results ✨") as step:
                step.output = f"```json\n{json.dumps(query_res, indent=2)}\n```"
            messages = [
                {"role": "user", "content": f"""The query you provided returned these results, summarize them:\n\n{json.dumps(query_res, indent=2)}"""},
                *cl.chat_context.to_openai(),
            ]
            query_success = True

@cl.set_starters
async def set_starters():
    return [
        cl.Starter(
            label="List Pathogens",
            message="Provide an extensive list of all the pathogens you are aware of and classify them",
        ),
        cl.Starter(
            label="Pathogens in China",
            message="Provide an extensive list of the pathogens that have been sequenced in China",
        ),
    ]