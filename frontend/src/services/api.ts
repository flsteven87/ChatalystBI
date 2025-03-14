// API service for communicating with the backend

// API base URL - can be configured based on environment
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

// 添加日誌記錄
console.log(`API_BASE_URL: ${API_BASE_URL}`);

// Types
export interface ImageInfo {
  id: string;
  url: string;
}

export interface ChatRequest {
  query: string;
  context?: Record<string, any>;
}

export interface ChatResponse {
  response: string;
  images: ImageInfo[];
}

// API client for chat endpoints
export const chatApi = {
  /**
   * Send a query to the chat API
   * @param query The user's query
   * @param context Optional context information
   * @returns The response from the AI agents
   */
  async sendQuery(query: string, context?: Record<string, any>): Promise<ChatResponse> {
    try {
      console.log(`Sending query to ${API_BASE_URL}/chat/query:`, { query, context });
      
      const response = await fetch(`${API_BASE_URL}/chat/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query, context } as ChatRequest),
      });

      console.log('Response status:', response.status);
      
      // 嘗試獲取響應文本，無論是否成功
      const responseText = await response.text();
      console.log('Response text:', responseText);
      
      if (!response.ok) {
        try {
          // 嘗試解析錯誤響應為 JSON
          const errorData = JSON.parse(responseText);
          throw new Error(errorData.detail || `Server error: ${response.status}`);
        } catch (parseError) {
          // 如果解析失敗，使用原始響應文本
          throw new Error(`Server error: ${response.status} - ${responseText}`);
        }
      }

      // 嘗試解析響應為 JSON
      let data;
      try {
        data = JSON.parse(responseText);
      } catch (parseError) {
        console.error('Error parsing response as JSON:', parseError);
        throw new Error(`Invalid JSON response: ${responseText}`);
      }
      
      console.log('Raw API response:', data);
      
      // 驗證響應格式
      if (!data.response) {
        console.error('Invalid response format - missing "response" field:', data);
        throw new Error('Invalid response format from server');
      }
      
      // Ensure images are properly formatted
      if (data.images && Array.isArray(data.images)) {
        console.log('Processing images in API response:', data.images);
      } else {
        console.log('No images in response or images is not an array');
        // 確保 images 是一個數組
        data.images = [];
      }
      
      return data;
    } catch (error) {
      console.error('Error sending chat query:', error);
      throw error;
    }
  },
};

// API client for image endpoints
export const imageApi = {
  /**
   * Get information about a specific image
   * @param imageId The ID of the image
   * @returns Information about the image
   */
  async getImageInfo(imageId: string): Promise<ImageInfo> {
    try {
      const response = await fetch(`${API_BASE_URL}/images/${imageId}`);

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to get image information');
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting image information:', error);
      throw error;
    }
  },

  /**
   * Get all available images
   * @returns List of all available images
   */
  async getAllImages(): Promise<ImageInfo[]> {
    try {
      const response = await fetch(`${API_BASE_URL}/images`);

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to get images');
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting all images:', error);
      throw error;
    }
  },

  /**
   * Get the full URL for an image
   * @param imageUrl The relative URL of the image
   * @returns The full URL of the image
   */
  getFullImageUrl(imageUrl: string): string {
    // 後端現在已經提供完整 URL，所以這個方法只是為了兼容性而保留
    // 如果 URL 已經是絕對路徑，直接返回
    if (imageUrl.startsWith('http')) {
      console.log(`URL is already absolute: ${imageUrl}`);
      return imageUrl;
    }
    
    // 如果是相對路徑，添加基礎 URL
    const baseUrl = API_BASE_URL.replace('/api/v1', '');
    const fullUrl = `${baseUrl}${imageUrl}`;
    console.log(`Converting ${imageUrl} to ${fullUrl}`);
    
    return fullUrl;
  }
};

// Export a default API object that includes all API services
const api = {
  chat: chatApi,
  image: imageApi,
};

export default api; 