"use client";

import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Send, Upload, FileText, Cloud, RefreshCw } from "lucide-react";

interface Message {
  id: string;
  content: string;
  role: "user" | "assistant";
  timestamp: Date;
}

export default function Home() {
  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      content: "Hello! I'm your college assistant. How can I help you today? You can ask me questions, upload documents (PDF/PPTX), or sync documents from Azure Files.",
      role: "assistant",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [isSyncing, setIsSyncing] = useState(false);
  const [isSyncingBlobs, setIsSyncingBlobs] = useState(false);
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    if (scrollAreaRef.current) {
      const scrollContainer = scrollAreaRef.current.querySelector('[data-radix-scroll-area-viewport]');
      if (scrollContainer) {
        scrollContainer.scrollTop = scrollContainer.scrollHeight;
      }
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: input.trim(),
      role: "user",
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    const currentInput = input.trim();
    setInput("");
    setIsLoading(true);

    try {
      // Create FormData for the FastAPI backend
      const formData = new FormData();
      formData.append('query', currentInput);

      // Call your FastAPI backend
      const response = await fetch(`${API_URL}/chat_simple/`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: data.response || "Sorry, I couldn't generate a response.",
        role: "assistant",
        timestamp: new Date(),
      };
      
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error calling backend:', error);
      
      // Fallback to dummy response if backend fails
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: "Sorry, I'm having trouble connecting to the server. Please try again later.",
        role: "assistant",
        timestamp: new Date(),
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Check file type
    if (!file.name.endsWith('.pdf') && !file.name.endsWith('.pptx')) {
      const errorMessage: Message = {
        id: Date.now().toString(),
        content: "Please upload only PDF or PPTX files.",
        role: "assistant",
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
      return;
    }

    setIsUploading(true);
    
    // Add upload message
    const uploadMessage: Message = {
      id: Date.now().toString(),
      content: `📄 Uploading document: ${file.name}`,
      role: "user",
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, uploadMessage]);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${API_URL}/upload_document/`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      const successMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: `✅ Document uploaded successfully! I can now answer questions about the content in "${file.name}".`,
        role: "assistant",
        timestamp: new Date(),
      };
      
      setMessages(prev => [...prev, successMessage]);
    } catch (error) {
      console.error('Error uploading document:', error);
      
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: "❌ Sorry, there was an error uploading your document. Please make sure the backend server is running.",
        role: "assistant",
        timestamp: new Date(),
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsUploading(false);
      // Clear the file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleAzureSync = async () => {
    setIsSyncing(true);
    
    // Add sync message
    const syncMessage: Message = {
      id: Date.now().toString(),
      content: "🔄 Syncing documents from Azure Files...",
      role: "assistant",
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, syncMessage]);

    try {
      const response = await fetch(`${API_URL}/sync_azure_files/`, {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      const successMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: `✅ ${data.message} You can now ask questions about all the documents stored in Azure Files.`,
        role: "assistant",
        timestamp: new Date(),
      };
      
      setMessages(prev => [...prev, successMessage]);
    } catch (error) {
      console.error('Error syncing Azure Files:', error);
      
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: "❌ Sorry, there was an error syncing documents from Azure Files. Please make sure Azure Files is properly configured and the backend server is running.",
        role: "assistant",
        timestamp: new Date(),
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsSyncing(false);
    }
  };

  const handleAzureBlobSync = async () => {
    setIsSyncingBlobs(true);
    
    // Add sync message
    const syncMessage: Message = {
      id: Date.now().toString(),
      content: "🔄 Syncing uploaded documents from Azure Blob Storage...",
      role: "assistant",
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, syncMessage]);

    try {
      const response = await fetch(`${API_URL}/sync_azure_blobs/`, {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      const successMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: `✅ ${data.message} You can now ask questions about all uploaded documents.`,
        role: "assistant",
        timestamp: new Date(),
      };
      
      setMessages(prev => [...prev, successMessage]);
    } catch (error) {
      console.error('Error syncing Azure blobs:', error);
      
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: "❌ Sorry, there was an error syncing documents from Azure Blob Storage. Please make sure the backend server is running.",
        role: "assistant",
        timestamp: new Date(),
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsSyncingBlobs(false);
    }
  };

  const getDummyResponse = (input: string): string => {
    const responses = [
      "I understand you're asking about: " + input + ". Let me help you with that!",
      "That's a great question! Based on what you've asked, here's what I can tell you...",
      "I'm here to help with your college-related queries. Could you provide more details about what you're looking for?",
      "Thanks for reaching out! I'd be happy to assist you with information about our college programs and services.",
    ];
    return responses[Math.floor(Math.random() * responses.length)];
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="flex flex-col h-screen bg-transparent text-foreground">
      {/* Header */}
      <div className=" p-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold">College Assistant</h1>
            <p className="text-sm text-muted-foreground">Your AI-powered college information bot</p>
          </div>
          <div className="flex items-center space-x-2">
            <Button
              onClick={handleAzureSync}
              disabled={isSyncing}
              variant="outline"
              size="sm"
              className="flex items-center space-x-2"
            >
              {isSyncing ? (
                <>
                  <RefreshCw className="h-4 w-4 animate-spin" />
                  <span>Syncing...</span>
                </>
              ) : (
                <>
                  <Cloud className="h-4 w-4" />
                  <span>Sync Azure Files</span>
                </>
              )}
            </Button>
            <Button
              onClick={handleAzureBlobSync}
              disabled={isSyncingBlobs}
              variant="outline"
              size="sm"
              className="flex items-center space-x-2"
            >
              {isSyncingBlobs ? (
                <>
                  <RefreshCw className="h-4 w-4 animate-spin" />
                  <span>Syncing...</span>
                </>
              ) : (
                <>
                  <Upload className="h-4 w-4" />
                  <span>Sync Uploads</span>
                </>
              )}
            </Button>
            <Button
              onClick={handleUploadClick}
              disabled={isUploading}
              variant="outline"
              size="sm"
              className="flex items-center space-x-2"
            >
              {isUploading ? (
                <>
                  <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin"></div>
                  <span>Uploading...</span>
                </>
              ) : (
                <>
                  <Upload className="h-4 w-4" />
                  <span>Upload Doc</span>
                </>
              )}
            </Button>
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.pptx"
              onChange={handleFileUpload}
              className="hidden"
            />
          </div>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-hidden">
        <ScrollArea ref={scrollAreaRef} className="h-full p-4">
          <div className="space-y-4 max-w-4xl mx-auto">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <Card
                  className={`max-w-[80%] p-4 ${
                    message.role === "user"
                      ? "bg-primary text-primary-foreground ml-12"
                      : "bg-muted mr-12"
                  }`}
                >
                  <div className="space-y-2">
                    <p className="text-sm leading-relaxed">{message.content}</p>
                    <p className="text-xs opacity-70">
                      {message.timestamp.toLocaleTimeString([], {
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                    </p>
                  </div>
                </Card>
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <Card className="max-w-[80%] p-4 bg-muted mr-12">
                  <div className="flex items-center space-x-2">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-current rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-current rounded-full animate-bounce" style={{ animationDelay: "0.1s" }}></div>
                      <div className="w-2 h-2 bg-current rounded-full animate-bounce" style={{ animationDelay: "0.2s" }}></div>
                    </div>
                    <span className="text-sm text-muted-foreground">Thinking...</span>
                  </div>
                </Card>
              </div>
            )}
          </div>
        </ScrollArea>
      </div>

      {/* Input Area */}
      <div className=" p-4">
        <div className="max-w-4xl mx-auto">
          <div className="flex space-x-2">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyPress}
              placeholder="Ask me anything about college..."
              className="flex-1"
              disabled={isLoading}
            />
            <Button
              onClick={handleSendMessage}
              disabled={!input.trim() || isLoading}
              size="icon"
            >
              <Send className="h-4 w-4" />
            </Button>
          </div>
          <p className="text-xs text-muted-foreground mt-2 text-center">
            Press Enter to send, Shift + Enter for new line • Upload documents or sync from Azure Files
          </p>
        </div>
      </div>
    </div>
  );
}
