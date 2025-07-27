import chromadb
import uuid
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
        # Generate unique IDs for each document chunk using UUID
        ids = [str(uuid.uuid4()) for _ in range(len(texts))]
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
        
        # Log query results for debugging
        if results and results['documents']:
            documents = results['documents'][0]
            metadatas = results.get('metadatas', [[]])[0]
            distances = results.get('distances', [[]])[0]
            
            print(f"📊 Query returned {len(documents)} documents:")
            for i, (doc, metadata, distance) in enumerate(zip(documents, metadatas, distances)):
                filename = metadata.get('filename', 'Unknown')
                source = metadata.get('source', 'Unknown')
                print(f"  {i+1}. {filename} (source: {source}, distance: {distance:.4f})")
        else:
            print("📊 No relevant documents found in ChromaDB")
        
        # Return the 'documents' field from the first (and only) query result
        # This will be a list of strings (the text chunks)
        return results['documents'][0] if results and results['documents'] else []
    
    def get_document_count(self) -> int:
        """
        Get the total number of documents in the collection.
        
        Returns:
            int: Total number of document chunks stored.
        """
        result = self.collection.count()
        return result
    
    def similarity_search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict]:
        """
        Performs similarity search and returns documents with metadata in the format expected by main.py.
        
        Args:
            query_embedding (List[float]): The embedding of the user's query.
            top_k (int): The number of top relevant documents to retrieve.
            
        Returns:
            List[Dict]: List of documents, each containing 'content' and 'metadata' keys.
        """
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            
            documents_with_metadata = []
            if results and results['documents']:
                documents = results['documents'][0]
                metadatas = results.get('metadatas', [[]])[0]
                distances = results.get('distances', [[]])[0]
                
                print(f"📊 Similarity search returned {len(documents)} documents:")
                for i, (doc, metadata, distance) in enumerate(zip(documents, metadatas, distances)):
                    filename = metadata.get('filename', 'Unknown')
                    source = metadata.get('source', 'Unknown')
                    print(f"  {i+1}. {filename} (source: {source}, distance: {distance:.4f})")
                    
                    documents_with_metadata.append({
                        'content': doc,
                        'metadata': metadata,
                        'distance': distance
                    })
            else:
                print("📊 No relevant documents found in ChromaDB")
            
            return documents_with_metadata
            
        except Exception as e:
            print(f"Error in similarity search: {e}")
            return []

    def get_documents_by_source(self, source: str) -> List[Dict]:
        """
        Get all documents from a specific source.
        
        Args:
            source (str): The source to filter by (e.g., 'user_upload', 'azure_files')
            
        Returns:
            List[Dict]: List of documents with their metadata.
        """
        try:
            results = self.collection.get(
                where={"source": source}
            )
            
            documents_info = []
            if results and results['documents']:
                for i, (doc, metadata) in enumerate(zip(results['documents'], results['metadatas'])):
                    documents_info.append({
                        'content': doc[:200] + "..." if len(doc) > 200 else doc,
                        'metadata': metadata
                    })
            
            return documents_info
            
        except Exception as e:
            print(f"Error getting documents by source {source}: {e}")
            return []

