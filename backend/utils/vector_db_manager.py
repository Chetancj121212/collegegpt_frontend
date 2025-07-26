import chromadb
from typing import List, Dict

class VectorDBManager:
    def __init__(self, db_path: str = "./chroma_db"):
        """
        Initializes the ChromaDB client.
        Data will be persisted to the specified db_path.

        Args:
            db_path (str): The file system path where ChromaDB will store its data.
        """
        # Initialize a persistent ChromaDB client
        self.client = chromadb.PersistentClient(path=db_path)
        # Get or create a collection to store our document chunks
        self.collection = self.client.get_or_create_collection(name="document_chunks")
        print(f"ChromaDB initialized. Data path: {db_path}")

    def add_documents(self, texts: List[str], embeddings: List[List[float]], metadatas: List[Dict]) -> None:
        """
        Adds documents (text chunks, their embeddings, and associated metadata)
        to the ChromaDB collection.

        Args:
            texts (List[str]): A list of text chunks.
            embeddings (List[List[float]]): A list of corresponding embeddings for the text chunks.
            metadatas (List[Dict]): A list of dictionaries, where each dictionary
                                    contains metadata for a corresponding text chunk.
        """
        # Generate simple unique IDs for each document chunk
        ids = [f"doc_{i}" for i in range(len(texts))]
        self.collection.add(
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        print(f"Added {len(texts)} document chunks to ChromaDB.")

    def query_documents(self, query_embedding: List[float], n_results: int = 5) -> List[str]:
        """
        Queries the vector database for relevant documents based on a query embedding.

        Args:
            query_embedding (List[float]): The embedding of the user's query.
            n_results (int): The number of top relevant documents to retrieve.

        Returns:
            List[str]: A list of text content from the most relevant document chunks.
        """
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
            # You can add 'where' clause here if you want to filter by metadata
            # where={"filename": "your_file.pdf"}
        )
        # Return the 'documents' field from the first (and only) query result
        # This will be a list of strings (the text chunks)
        return results['documents'][0] if results and results['documents'] else []

