from utils.vector_db_manager import VectorDBManager

db_manager = VectorDBManager()
result = db_manager.collection.get()

print(f'Total documents in ChromaDB: {len(result["documents"])}')

# Check for uploaded documents specifically
uploaded_docs = []
for i, metadata in enumerate(result['metadatas']):
    if metadata.get('source') == 'user_upload':
        uploaded_docs.append({
            'index': i,
            'filename': metadata.get('filename'),
            'source': metadata.get('source'),
            'storage_location': metadata.get('storage_location')
        })

print(f'User uploaded documents in ChromaDB: {len(uploaded_docs)}')
for doc in uploaded_docs:
    print(f'  - {doc["filename"]} from {doc["source"]}')

# Check for any documents with Azure blob references
azure_docs = []
for i, metadata in enumerate(result['metadatas']):
    if 'blob_url' in metadata or 'Azure Blob' in str(metadata.get('storage_location', '')):
        azure_docs.append({
            'index': i,
            'filename': metadata.get('filename'),
            'storage_location': metadata.get('storage_location'),
            'blob_url': metadata.get('blob_url')
        })

print(f'Documents with Azure references: {len(azure_docs)}')
for doc in azure_docs:
    print(f'  - {doc["filename"]} at {doc["storage_location"]}')
