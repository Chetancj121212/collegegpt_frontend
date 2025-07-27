# Azure Files Integration Setup Guide

This guide will help you integrate your existing PDF documents stored in Microsoft Azure Files with your College Assistant Chatbot.

## 📋 Prerequisites

1. **Azure Storage Account** with Files service enabled
2. **Azure Files Share** containing your PDF documents
3. **Connection String** for your Azure Storage Account

## 🔧 Azure Storage Setup

### Step 1: Get Your Azure Storage Connection String

1. Go to the [Azure Portal](https://portal.azure.com)
2. Navigate to your Storage Account
3. Go to **Security + networking** → **Access keys**
4. Copy the **Connection string** from either key1 or key2

### Step 2: Verify Your File Share

1. In your Storage Account, go to **Data storage** → **File shares**
2. Note the name of your file share containing PDF documents
3. Ensure your PDF files are uploaded and accessible

### Step 3: Configure Backend Environment

Update your backend `.env` file:

```env
# Existing configuration
GEMINI_API_KEY="your_gemini_api_key"

# Azure Files Configuration
AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=yourstorageaccount;AccountKey=your_account_key;EndpointSuffix=core.windows.net"
AZURE_FILES_SHARE_NAME="your-file-share-name"
```

**Replace:**
- `yourstorageaccount` with your actual storage account name
- `your_account_key` with your actual account key
- `your-file-share-name` with your actual file share name

## 🚀 Usage

### Option 1: Sync All Documents (Recommended)

1. Start your backend server
2. In the chat interface, click the **"Sync Azure"** button
3. Wait for the sync to complete
4. All PDF documents will be processed and available for Q&A

### Option 2: API Endpoints

You can also use the following API endpoints directly:

#### Sync All Documents
```bash
POST http://localhost:8000/sync_azure_files/
```

#### List Available Documents
```bash
GET http://localhost:8000/azure_files/list
```

#### Check System Status
```bash
GET http://localhost:8000/system/status
```

## 📁 File Organization

### Supported Structure
```
your-file-share/
├── document1.pdf
├── folder1/
│   ├── document2.pdf
│   └── document3.pdf
└── folder2/
    └── subfolder/
        └── document4.pdf
```

### Features
- **Recursive scanning**: Finds PDFs in all subdirectories
- **Automatic processing**: Extracts text and creates embeddings
- **Metadata preservation**: Keeps track of file paths and sources
- **Incremental updates**: Only processes new/changed files

## 🔍 How It Works

1. **Discovery**: Scans your Azure Files share for PDF documents
2. **Download**: Temporarily downloads each PDF for processing
3. **Text Extraction**: Extracts text content from each PDF
4. **Chunking**: Splits text into manageable chunks for better search
5. **Embedding**: Converts text chunks into vector embeddings
6. **Storage**: Stores embeddings in ChromaDB vector database
7. **Cleanup**: Removes temporary files after processing

## 🛠 Troubleshooting

### Common Issues

#### Connection String Issues
```
Error: Azure Files integration not configured
```
**Solution**: Verify your connection string is correct and properly formatted.

#### File Share Not Found
```
Error: Directory not found
```
**Solution**: Check that your file share name is correct and exists.

#### Permission Issues
```
Error: Access denied
```
**Solution**: Ensure your storage account key has proper permissions.

#### Large File Processing
```
Error: Timeout during processing
```
**Solution**: Consider processing files in smaller batches or increasing timeout limits.

### Debug Steps

1. **Check system status**:
   ```bash
   GET http://localhost:8000/system/status
   ```

2. **List available files**:
   ```bash
   GET http://localhost:8000/azure_files/list
   ```

3. **Check backend logs** for detailed error messages

## 🔒 Security Best Practices

1. **Use SAS tokens** instead of account keys when possible
2. **Limit access** to specific file shares only
3. **Rotate keys regularly** in production environments
4. **Use Azure Key Vault** for storing connection strings in production
5. **Monitor access logs** for unusual activity

## 💡 Tips for Optimal Performance

1. **Organize files** in logical folder structures
2. **Use descriptive filenames** for better organization
3. **Keep PDFs text-searchable** (not scanned images)
4. **Limit file sizes** to reasonable limits (< 50MB per PDF)
5. **Run sync during off-peak hours** for large document sets

## 🔄 Updating Documents

### Adding New Documents
1. Upload new PDFs to your Azure Files share
2. Click **"Sync Azure"** in the chat interface
3. Only new documents will be processed

### Removing Documents
1. Delete PDFs from your Azure Files share
2. Restart the backend to clear old references
3. Run sync again to update the database

## 📊 Monitoring and Analytics

### Available Metrics
- Number of documents processed
- Processing time per document
- Vector database size
- Query performance

### Logging
Check backend logs for:
- Sync progress
- Error messages
- Performance metrics
- File processing status

---

**Need help?** Check the main README.md or create an issue in the repository.
