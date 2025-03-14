import { ReactNode, useEffect, useState } from 'react';
import ReactMarkdown from 'react-markdown';
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
  // 添加一個狀態來存儲圖片測試結果
  const [imageTestResults, setImageTestResults] = useState<Record<string, any>>({});
  // 添加一個狀態來存儲直接訪問的 URL
  const [directImageUrls, setDirectImageUrls] = useState<Record<string, string>>({});
  
  // 測試圖片訪問的函數
  const testImageAccess = async (imageId: string) => {
    try {
      console.log(`Testing access for image ${imageId}`);
      const response = await fetch(`http://localhost:8000/api/v1/images/test-access/${imageId}`);
      const data = await response.json();
      console.log(`Test result for image ${imageId}:`, data);
      
      // 更新測試結果
      setImageTestResults(prev => ({...prev, [imageId]: data}));
      
      return data;
    } catch (error) {
      console.error(`Error testing image ${imageId}:`, error);
      // 更新測試結果
      setImageTestResults(prev => ({...prev, [imageId]: {status: 'error', message: String(error)}}));
      return {status: 'error', message: String(error)};
    }
  };
  
  // 獲取直接訪問 URL 的函數
  const getDirectImageUrl = (imageId: string) => {
    return `http://localhost:8000/api/v1/images/direct/${imageId}`;
  };
  
  // Effect to process images when the message changes
  useEffect(() => {
    if (message.images && message.images.length > 0) {
      console.log('Processing images in ChatMessage:', message.images);
      
      // 初始化所有圖片的加載狀態為 loading
      const initialStatus: Record<string, 'loading' | 'success' | 'error'> = {};
      const directUrls: Record<string, string> = {};
      
      message.images.forEach(image => {
        initialStatus[image.id] = 'loading';
        // 生成直接訪問 URL
        directUrls[image.id] = getDirectImageUrl(image.id);
      });
      
      setImageLoadStatus(initialStatus);
      setDirectImageUrls(directUrls);
      
      // 預加載圖片以檢查它們是否可訪問
      message.images.forEach(image => {
        console.log(`Image ${image.id} URL: ${image.url}`);
        console.log(`Direct Image URL: ${getDirectImageUrl(image.id)}`);
        
        // 多嘗試幾種方式
        const urls = [
          image.url,  // 原始 URL
          getDirectImageUrl(image.id),  // 直接訪問 URL
          `http://localhost:8000/static/images/${image.id}.png`,  // 直接構造的靜態文件 URL
          `http://localhost:8000/static/images/${image.id}.png?t=${Date.now()}`  // 帶時間戳的 URL
        ];
        
        // 嘗試所有 URL
        Promise.all(urls.map(url => 
          fetch(url)
            .then(response => {
              console.log(`Fetch response for URL ${url}:`, response.status, response.statusText);
              if (!response.ok) {
                return Promise.reject(`HTTP error! Status: ${response.status}`);
              }
              return response.blob();
            })
            .then(blob => ({url, success: true, size: blob.size}))
            .catch(error => ({url, success: false, error}))
        )).then(results => {
          console.log(`Fetch results for image ${image.id}:`, results);
          
          // 如果至少有一個成功，標記為成功
          const successResult = results.find(r => r.success);
          if (successResult) {
            console.log(`Successfully loaded image ${image.id} with URL ${successResult.url}`);
            setImageLoadStatus(prev => ({...prev, [image.id]: 'success'}));
            // 如果成功的 URL 不是原始 URL，更新 directImageUrls
            if (successResult.url !== image.url) {
              setDirectImageUrls(prev => ({...prev, [image.id]: successResult.url}));
            }
          } else {
            console.error(`Failed to load image ${image.id} with all URLs`);
            setImageLoadStatus(prev => ({...prev, [image.id]: 'error'}));
          }
        });
      });
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
                  console.log(`Rendering image ${image.id} with URL: ${image.url}`);
                  console.log(`Image load status: ${imageLoadStatus[image.id] || 'unknown'}`);
                  console.log(`Direct image URL: ${directImageUrls[image.id] || 'none'}`);
                  
                  // 使用直接訪問 URL 或原始 URL
                  const imageUrl = directImageUrls[image.id] || image.url;
                  
                  return (
                    <div key={image.id} className={styles.imageWrapper}>
                      {/* 顯示圖片加載狀態 */}
                      {imageLoadStatus[image.id] === 'loading' && (
                        <div className={styles.imageLoading}>圖片加載中...</div>
                      )}
                      
                      {/* 使用 img 標籤加載圖片 */}
                      <img 
                        src={imageUrl} 
                        alt="Generated visualization" 
                        className={styles.responseImage}
                        style={{display: imageLoadStatus[image.id] === 'error' ? 'none' : 'block'}}
                        onError={(e) => {
                          console.error(`Error loading image ${image.id}:`, e);
                          console.error(`Image URL was: ${imageUrl}`);
                          // 更新圖片加載狀態
                          setImageLoadStatus(prev => ({...prev, [image.id]: 'error'}));
                          
                          // Fallback to a placeholder if image fails to load
                          (e.target as HTMLImageElement).src = 'https://via.placeholder.com/400x300?text=Image+Loading+Failed';
                          
                          // Try to fetch the image directly to see if there's a CORS or other issue
                          fetch(imageUrl)
                            .then(response => {
                              if (!response.ok) {
                                console.error(`Fetch failed with status: ${response.status}`);
                                return response.text().then(text => {
                                  console.error(`Error response: ${text}`);
                                  return `Error: ${response.status}`;
                                });
                              }
                              return response.blob().then(blob => {
                                console.log('Fetch succeeded, blob size:', blob.size);
                                return 'Success';
                              });
                            })
                            .then(result => console.log('Fetch result:', result))
                            .catch(fetchError => console.error('Fetch error:', fetchError));
                        }}
                        onLoad={() => {
                          console.log(`Image ${image.id} loaded successfully`);
                          // 更新圖片加載狀態
                          setImageLoadStatus(prev => ({...prev, [image.id]: 'success'}));
                        }}
                      />
                      
                      {/* 如果圖片加載失敗，顯示錯誤信息和替代方案 */}
                      {imageLoadStatus[image.id] === 'error' && (
                        <div className={styles.imageError}>
                          <p>圖片加載失敗</p>
                          <p>嘗試使用多種方式加載：</p>
                          <div className={styles.imageFallbacks}>
                            {/* 原始 URL */}
                            <div className={styles.imageFallback}>
                              <h4>原始 URL:</h4>
                              <img 
                                src={image.url} 
                                alt="Original URL" 
                                className={styles.fallbackImage}
                                onError={(e) => console.error(`Error loading image from original URL:`, e)}
                              />
                            </div>
                            
                            {/* 直接訪問 URL */}
                            <div className={styles.imageFallback}>
                              <h4>直接訪問 URL:</h4>
                              <img 
                                src={getDirectImageUrl(image.id)} 
                                alt="Direct URL" 
                                className={styles.fallbackImage}
                                onError={(e) => console.error(`Error loading image from direct URL:`, e)}
                              />
                            </div>
                            
                            {/* 使用 iframe */}
                            <div className={styles.imageFallback}>
                              <h4>使用 iframe:</h4>
                              <iframe 
                                src={getDirectImageUrl(image.id)} 
                                style={{width: '100%', height: '200px', border: 'none'}}
                                title={`Image ${image.id}`}
                              />
                            </div>
                          </div>
                        </div>
                      )}
                      
                      <div className={styles.imageCaption}>
                        圖表 ID: {image.id}
                      </div>
                      
                      {/* 添加直接鏈接到圖片，方便用戶手動查看 */}
                      <div className={styles.imageLinks}>
                        <a href={image.url} target="_blank" rel="noopener noreferrer">
                          原始 URL 查看
                        </a>
                        <a 
                          href={getDirectImageUrl(image.id)} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          style={{marginLeft: '10px'}}
                        >
                          直接訪問 URL 查看
                        </a>
                        <a 
                          href={`http://localhost:8000/static/images/${image.id}.png`} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          style={{marginLeft: '10px'}}
                        >
                          靜態路徑查看
                        </a>
                      </div>
                      
                      {/* 添加測試按鈕 */}
                      <div className={styles.imageDebug}>
                        <button 
                          onClick={() => testImageAccess(image.id)}
                          className={styles.debugButton}
                        >
                          測試圖片訪問
                        </button>
                        
                        {/* 顯示測試結果 */}
                        {imageTestResults[image.id] && (
                          <div className={styles.debugResult}>
                            <h4>測試結果：</h4>
                            <pre>{JSON.stringify(imageTestResults[image.id], null, 2)}</pre>
                          </div>
                        )}
                      </div>
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