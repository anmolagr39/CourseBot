import google.generativeai as genai
from groq import Groq
import chromadb

genai.configure(api_key='AIzaSyAwA_IGX-SdGu_b_lDMrVqSfzLGgYYYnKs')
model = genai.GenerativeModel('gemini-1.5-pro')

fixed_prefix = """
You are a course information extractor. Your task is to identify and return ONLY the course name, course code, 
or course shortform from the user's question about a college course. Do not provide any other information or explanation. 
Just return the extracted course identifier.
Examples:
1. Input: Who is the instructor in charge of CHEM F111? Output: CHEM F111 
2. Input: What are the prerequisites for General Chemistry? Output: General Chemistry 
3. Input: When does the class for genchem start? Output: genchem 

If you are unable to identify any of the course name/code/shortform, return None.
Now, extract the course identifier from the following question:
"""

def get_gemini_response(user_prompt):
    try:
        full_prompt = fixed_prefix + "\n" + user_prompt.strip()

        response = model.generate_content(full_prompt)

        return response.text.strip()
    except Exception as e:
        return f"Error: {str(e)}"

client = chromadb.HttpClient()

def get_collection(client, collection_name):
    collections = client.list_collections()

    # Check if the collection exists
    for coll in collections:
        if coll.name == collection_name:
            print(f"Using the existing collection: {collection_name}")
            return coll

    raise ValueError(f"Collection '{collection_name}' does not exist.")

# Get the existing collection
collection_name = "Check11"
collection = get_collection(client, collection_name)

# Function to query Chroma DB and return the text content of the results
def query_chroma_db(query_text, n_result=1):
    results = collection.query(
        query_texts=[query_text],  # Provide the query text from Gemini
        n_results=n_result,
        include=["metadatas"]
         # Specify how many results to return
    )

    # Extract and return only the text content of the results
    return [doc[0]['source'] for doc in results['metadatas']]

# Step 3: Groq LLaMA 3 API Call (Using Groq to process the query and Chroma DB result)
def process_with_llama3(original_query, chroma_db_content):
    # If chroma_db_content is a list, we join the list into a string
    if isinstance(chroma_db_content, list):
        chroma_db_content = " ".join(chroma_db_content)

    # Combine the original query with the content retrieved from Chroma DB
    final_input =   chroma_db_content + "based on the info above" + original_query

    # Hardcoded Groq API key
    client = Groq(api_key="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")

    try:
        # Groq API call for LLaMA 3 model
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": final_input,  # Using final_input as the prompt
                }
            ],
            model="llama3-70b-8192",  # Specifying the model
        )

        # Return the generated response from the Groq API
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# Step 4: Merged Pipeline (Gemini + Chroma DB + Groq LLaMA 3)
def query_pipeline(user_query, last_context=None):
    # 1. Condense the query using Gemini API
    condensed_query = get_gemini_response(user_query)

    # If Gemini returns a new identifier, update the context
    if condensed_query != "None":
        print(f"New course identifier detected: {condensed_query}")
        # 2. Query Chroma DB using the condensed query
        chroma_results = query_chroma_db(condensed_query)

        if not chroma_results:
            return "No relevant documents found in Chroma DB."

        # Use the first document returned from Chroma DB
        chroma_db_content = chroma_results[0]

        # Update the last context with the new one
        last_context = chroma_db_content
    else:
        # If no new course identifier is found, use the previous context
        if last_context is not None or last_context != "none":
            print("No new course identifier found, using previous context.")
            chroma_db_content = last_context
        else:
            return "No previous context found and no new course identifier detected."

    # 3. Process the combined original query and Chroma DB content using Groq LLaMA 3 model
    print(user_query,condensed_query)
    final_output = process_with_llama3(user_query, chroma_db_content)

    return final_output, last_context  # Return both the output and the context


# Step 5: Running the Pipeline
last_context = None  # To store the last context

while True:
    user_input = input("Enter your query (type 'exit' to stop): ")

    # If the user types 'exit', stop the program
    if user_input.lower() == "exit":
        print("Exiting the program.")
        break

    # Get the final response from the pipeline and update the context
    result, last_context = query_pipeline(user_input, last_context)
    print(result)
