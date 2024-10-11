import os
import chromadb

# Initialize Chroma HTTP Client (replace with the correct host and port if needed)
client = chromadb.HttpClient()


# Function to get or create a collection
def get_or_create_collection(client, collection_name):
    # Get the list of collections
    collections = client.list_collections()

    # Check if the collection already exists
    for coll in collections:
        if coll.name == collection_name:
            print(f"Collection '{collection_name}' already exists. Using the existing collection.")
            return coll  # Return the existing collection

    # If the collection doesn't exist, create it
    print(f"Creating new collection: {collection_name}")
    return client.create_collection(collection_name, metadata={"hnsw:space": "cosine"})


# Get or create the collection
collection_name = "Check11"
collection = get_or_create_collection(client, collection_name)


# Function to check if a document with the same name already exists in Chroma DB
def document_exists_in_chroma(collection, document_id):
    try:
        # Try to get the document by its ID (file name)
        result = collection.get(ids=[document_id])
        return len(result["documents"]) > 0  # If the document exists, the list will not be empty
    except Exception as e:
        # If there's any error (like the document doesn't exist), return False
        return False


# Function to read files from a directory and add only new files to Chroma DB
def store_text_files_in_chroma(directory_path):
    # List to store file contents and their metadata
    documents = []
    metadatas = []
    ids = []

    # Get all files from the directory
    for filename in os.listdir(directory_path):
        if filename.endswith(".txt"):  # Ensure we are only processing text files
            file_id = filename  # Use the file name as the ID

            # Check if the file is already in the collection
            if not document_exists_in_chroma(collection, file_id):
                file_path = os.path.join(directory_path, filename)
                with open(file_path, "r", encoding="utf-8") as file:
                    # Read the file content
                    file_content = file.read()

                    # Use the file name (without extension) as the key and the content as the value
                    documents.append(filename)
                    metadatas.append({"source": file_content})  # Add metadata for each document
                    ids.append(file_id)  # Use the file name as the unique document ID
            else:
                print(f"File '{filename}' already exists in the collection. Skipping...")

    # Add the documents to the Chroma DB collection if there are new files
    if documents:
        collection.add(
            documents=documents,  # Add all the document contents
            metadatas=metadatas,  # Add metadata (file names)
            ids=ids  # Add file names as unique document IDs
        )
        print(f"Added {len(documents)} new files to Chroma DB collection")
    else:
        print("No new files to add.")


# Specify the directory containing the text files
directory_path = r"C:\\Users\\welcome\\Downloads\\pythonProject18\\pythonProject18\\output"

# Call the function to store only new text files in Chroma DB
store_text_files_in_chroma(directory_path)
