'use client';

import { useState, useEffect, useRef } from 'react';
import { v4 as uuidv4 } from 'uuid';
import ChatInput from './ChatInput';
import ChatMessage, { Message } from './ChatMessage';
import api, { ImageInfo } from '@/services/api';
import styles from './ChatContainer.module.css';

export default function ChatContainer() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async (content: string) => {
    // Add user message to the chat
    const userMessage: Message = {
      id: uuidv4(),
      content,
      role: 'user',
    };
    
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    // Add a loading message
    const loadingMessageId = uuidv4();
    const loadingMessage: Message = {
      id: loadingMessageId,
      content: '正在思考中...',
      role: 'system',
    };
    
    setMessages((prev) => [...prev, loadingMessage]);

    try {
      console.log('Sending message to API:', content);
      
      // Send the message to the API
      const response = await api.chat.sendQuery(content);
      
      // Log the response for debugging
      console.log('API Response:', response);
      
      // Check if images are included in the response
      if (response.images && response.images.length > 0) {
        console.log('Images found in response:', response.images);
      } else {
        console.log('No images found in response');
      }
      
      // Remove the loading message and add the real response
      setMessages((prev) => 
        prev.filter(msg => msg.id !== loadingMessageId).concat({
          id: uuidv4(),
          content: response.response,
          role: 'system',
          images: response.images,
        })
      );
    } catch (error) {
      console.error('Error sending message:', error);
      
      // 嘗試獲取更詳細的錯誤信息
      let errorMessage = '抱歉，處理您的請求時發生錯誤。請稍後再試。';
      
      if (error instanceof Error) {
        console.error('Error details:', error.message);
        errorMessage = `錯誤: ${error.message}`;
      }
      
      // Remove the loading message and add an error message
      setMessages((prev) => 
        prev.filter(msg => msg.id !== loadingMessageId).concat({
          id: uuidv4(),
          content: errorMessage,
          role: 'system',
        })
      );
    } finally {
      setIsLoading(false);
    }
  };

  // Function to test image display
  const handleTestImageDisplay = async () => {
    try {
      // Fetch all available images using the API service
      const images = await api.image.getAllImages();
      
      if (images && images.length > 0) {
        console.log('Test: Found images:', images);
        
        // Add a test message with the first image
        setMessages((prev) => [...prev, {
          id: uuidv4(),
          content: '這是一個測試訊息，用於顯示圖片。',
          role: 'system',
          images: images.slice(0, 1), // Just use the first image
        }]);
      } else {
        console.log('Test: No images found');
        
        // Add a message indicating no images were found
        setMessages((prev) => [...prev, {
          id: uuidv4(),
          content: '沒有找到任何圖片。請先生成一些圖片再測試。',
          role: 'system',
        }]);
      }
    } catch (error) {
      console.error('Error testing image display:', error);
      
      // Add an error message
      setMessages((prev) => [...prev, {
        id: uuidv4(),
        content: '測試圖片顯示時發生錯誤。',
        role: 'system',
      }]);
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.messagesContainer}>
        {messages.length === 0 ? (
          <div className={styles.emptyState}>
            <p>發送一條消息開始對話</p>
            <button 
              className={styles.testButton}
              onClick={handleTestImageDisplay}
            >
              測試圖片顯示
            </button>
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <ChatMessage key={message.id} message={message} />
            ))}
            <div className={styles.testButtonContainer}>
              <button 
                className={styles.testButton}
                onClick={handleTestImageDisplay}
              >
                測試圖片顯示
              </button>
            </div>
          </>
        )}
        <div ref={messagesEndRef} />
      </div>
      <ChatInput onSendMessage={handleSendMessage} isLoading={isLoading} />
    </div>
  );
} 