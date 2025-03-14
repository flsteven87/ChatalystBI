import { ReactNode, useEffect, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import Image from 'next/image';
import styles from './ChatMessage.module.css';
import api, { ImageInfo } from '@/services/api';

export type MessageRole = 'user' | 'system';

export interface Message {
  id: string;
  content: string;
  role: MessageRole;
  images?: ImageInfo[];
}

interface ChatMessageProps {
  message: Message;
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user';
  // 添加一個狀態來跟踪圖片加載狀態
  const [imageLoadStatus, setImageLoadStatus] = useState<Record<string, 'loading' | 'success' | 'error'>>({});
  // 簡化狀態管理，只保留一個直接訪問的 URL 狀態
  const [imageUrls, setImageUrls] = useState<Record<string, string>>({});
  
  // Effect to process images when the message changes
  useEffect(() => {
    if (message.images && message.images.length > 0) {
      console.log('Processing images in ChatMessage:', message.images);
      
      // 初始化所有圖片的加載狀態為 loading
      const initialStatus: Record<string, 'loading' | 'success' | 'error'> = {};
      const urls: Record<string, string> = {};
      
      message.images.forEach(image => {
        initialStatus[image.id] = 'loading';
        
        // 使用直接訪問的端點 URL，這是最可靠的方式
        const directUrl = `http://localhost:8000/api/v1/images/direct/${image.id}`;
        
        urls[image.id] = directUrl;
        console.log(`Setting image ${image.id} URL to: ${directUrl}`);
      });
      
      setImageLoadStatus(initialStatus);
      setImageUrls(urls);
    }
  }, [message.images]);

  // Function to clean markdown content by removing any ![...](data:image/...) patterns
  // This prevents ReactMarkdown from trying to render base64 images
  const cleanMarkdownContent = (content: string) => {
    // Remove any markdown image syntax with data URLs or example.com URLs
    return content.replace(/!\[.*?\]\((?:data:image\/[^;]+;base64,[^)]+|https?:\/\/example\.com\/[^)]+)\)/g, '');
  };

  return (
    <div
      className={`${styles.messageContainer} ${
        isUser ? styles.userMessage : styles.systemMessage
      }`}
    >
      <div
        className={`${styles.messageContent} ${
          isUser ? styles.userMessageContent : styles.systemMessageContent
        }`}
      >
        {isUser ? (
          <div className={styles.messageText}>{message.content}</div>
        ) : (
          <div className={styles.markdownContent}>
            <ReactMarkdown>{cleanMarkdownContent(message.content)}</ReactMarkdown>
            
            {/* Display images if available */}
            {message.images && message.images.length > 0 && (
              <div className={styles.imagesContainer}>
                <h3>生成的視覺化圖表</h3>
                {message.images.map((image) => {
                  const imageUrl = imageUrls[image.id] || image.url;
                  console.log(`Rendering image ${image.id} with URL: ${imageUrl}`);
                  
                  return (
                    <div key={image.id} className={styles.imageWrapper}>
                      {/* 顯示圖片加載狀態 */}
                      {imageLoadStatus[image.id] === 'loading' && (
                        <div className={styles.imageLoading}>圖片加載中...</div>
                      )}
                      
                      {/* 顯示圖片 */}
                      {imageLoadStatus[image.id] !== 'error' ? (
                        // 使用普通 img 標籤，因為我們需要更好地控制錯誤處理
                        // Next/Image 元件對外部圖片需要更多配置且對錯誤處理不夠靈活
                        <img
                          src={imageUrl}
                          alt="Generated visualization"
                          className={styles.responseImage}
                          onError={(e) => {
                            console.error(`Error loading image ${image.id}:`, e);
                            console.error(`Failed image URL: ${imageUrl}`);
                            setImageLoadStatus(prev => ({...prev, [image.id]: 'error'}));
                            
                            // 嘗試使用靜態文件 URL 作為備用方案
                            const staticUrl = `http://localhost:8000/static/images/${image.id}.png?t=${Date.now()}`;
                            console.log(`Trying fallback URL: ${staticUrl}`);
                            
                            // 如果當前 URL 不是靜態 URL，嘗試使用靜態 URL
                            if (imageUrl !== staticUrl) {
                              setImageUrls(prev => ({...prev, [image.id]: staticUrl}));
                              // 重置為加載狀態，因為我們要嘗試新的 URL
                              setImageLoadStatus(prev => ({...prev, [image.id]: 'loading'}));
                              (e.target as HTMLImageElement).src = staticUrl;
                            } else {
                              // 如果靜態 URL 也失敗，使用備用圖片
                              (e.target as HTMLImageElement).src = 'https://via.placeholder.com/400x300?text=Image+Loading+Failed';
                            }
                          }}
                          onLoad={() => {
                            console.log(`Image ${image.id} loaded successfully with URL: ${imageUrl}`);
                            setImageLoadStatus(prev => ({...prev, [image.id]: 'success'}));
                          }}
                        />
                      ) : (
                        <div className={styles.imageError}>
                          <p>圖片加載失敗</p>
                          <button 
                            onClick={() => {
                              // 嘗試重新載入圖片
                              setImageLoadStatus(prev => ({...prev, [image.id]: 'loading'}));
                              const newUrl = `http://localhost:8000/api/v1/images/direct/${image.id}?t=${Date.now()}`;
                              setImageUrls(prev => ({...prev, [image.id]: newUrl}));
                            }}
                            className={styles.retryButton}
                          >
                            重試
                          </button>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
} 