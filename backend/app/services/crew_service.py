from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
import os
import re
from dotenv import load_dotenv
from app.tools.visualization_tools import create_line_chart, create_multi_line_chart
from app.schemas.chat import ImageInfo
import time

# 獲取基礎 URL - 優先使用環境變量，否則使用默認值
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
# 移除 API 版本路徑，如果存在
if BASE_URL.endswith("/api/v1"):
    BASE_URL = BASE_URL[:-7]

# Load environment variables
load_dotenv()

class CrewService:
    """Service for managing CrewAI operations."""
    
    def __init__(self):
        """Initialize the CrewAI service with OpenAI model."""
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                print("WARNING: OPENAI_API_KEY environment variable is not set")
                
            print(f"Initializing CrewService with API key: {api_key[:5]}..." if api_key else "Initializing CrewService without API key")
            
            self.llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.1,
                api_key=api_key
            )
            
            print("CrewService initialized successfully")
        except Exception as e:
            print(f"Error initializing CrewService: {str(e)}")
            raise
    
    def create_data_consultant_agent(self):
        """Create a data consultant agent that communicates with users and delegates tasks."""
        return Agent(
            role="Data Consultant",
            goal="Understand user needs, delegate analysis tasks, and communicate results effectively",
            backstory="""You are a seasoned data consultant with over 15 years of experience working with Fortune 500 companies. 
            Your expertise lies in translating business questions into data queries and coordinating complex analytics projects. 
            You excel at understanding client needs, communicating technical concepts in accessible language, 
            and ensuring that data analysis delivers actionable business insights. 
            Your background includes an MBA and a Master's in Data Science, giving you the perfect blend of business acumen and technical knowledge.""",
            verbose=True,
            llm=self.llm,
            allow_delegation=True,  # 允許委派任務
            max_iter=5,  # 限制最大迭代次數
            # 添加管理者的特殊說明
            agent_executor_kwargs={
                "system_message": """You are a data consultant manager who coordinates the work of data analysts.
                Your job is to understand the user's query, delegate analysis tasks to your team, and then review their work.
                
                IMPORTANT: You should NEVER perform data analysis or create visualizations yourself.
                Always delegate these tasks to your Data Analyst team member.
                
                When your analysts create visualizations, they will include Image IDs in their response.
                You MUST include these exact Image IDs in your final response without changing their format.
                The correct format is: "Image ID: [uuid]" (e.g., "Image ID: 123e4567-e89b-12d3-a456-426614174000")
                
                DO NOT convert these Image IDs into URLs or markdown image links.
                DO NOT modify the Image ID format in any way.
                DO NOT remove the "Image ID: " prefix.
                """
            }
        )
    
    def create_data_analyst_agent(self):
        """Create a data analyst agent that performs data analysis tasks."""
        return Agent(
            role="Data Analyst",
            goal="Analyze data thoroughly and produce accurate, insightful results",
            backstory="""You are an expert data analyst with a strong background in statistics, data visualization, and business intelligence. 
            You have worked across multiple industries including finance, healthcare, and e-commerce, giving you broad domain knowledge. 
            Your analytical skills are exceptional - you can identify patterns, outliers, and insights that others miss. 
            You're proficient with various data analysis methodologies and can adapt your approach based on the specific requirements of each task. 
            You take pride in producing clear, accurate analyses that drive business decisions.""",
            verbose=True,
            llm=self.llm,
            tools=[create_line_chart, create_multi_line_chart]
        )
    
    def create_task(self, agent, description, expected_output):
        """Create a task for an agent."""
        return Task(
            description=description,
            expected_output=expected_output,
            agent=agent
        )
    
    def extract_image_ids(self, text):
        """Extract image IDs from the agent's response.
        
        Args:
            text (str): The agent's response text
            
        Returns:
            list: A list of image IDs extracted from the text
        """
        # 處理 None 或空字符串
        if text is None or text.strip() == "":
            print("Warning: Empty text provided to extract_image_ids")
            return []
            
        # List to store all found image IDs
        all_image_ids = []
        
        print(f"Extracting image IDs from text: {text[:200]}...")  # Print first 200 chars for debugging
        
        # 主要模式：標準格式 "Image ID: [uuid]"
        pattern1 = r"Image ID: ([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})"
        matches1 = re.findall(pattern1, text)
        if matches1:
            print(f"Found {len(matches1)} image IDs using standard pattern: {matches1}")
            all_image_ids.extend(matches1)
        
        # 如果沒有找到標準格式，嘗試其他可能的格式
        if not all_image_ids:
            # 嘗試找出任何 UUID 格式的字符串
            pattern2 = r"([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})"
            matches2 = re.findall(pattern2, text)
            if matches2:
                print(f"Found {len(matches2)} potential image IDs using fallback pattern: {matches2}")
                # 驗證這些是否真的是圖片 ID
                verified_ids = []
                for image_id in matches2:
                    image_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "images", f"{image_id}.png")
                    if os.path.exists(image_path):
                        verified_ids.append(image_id)
                
                if verified_ids:
                    print(f"Verified {len(verified_ids)} image IDs: {verified_ids}")
                    all_image_ids.extend(verified_ids)
        
        # 移除重複項並保持順序
        unique_image_ids = []
        for image_id in all_image_ids:
            if image_id not in unique_image_ids:
                unique_image_ids.append(image_id)
        
        if unique_image_ids:
            print(f"Final extracted image IDs: {unique_image_ids}")
        else:
            print("No image IDs found in the response")
            
        return unique_image_ids
    
    async def process_query_with_crew(self, query, context=None):
        """Process a BI query using multiple CrewAI agents.
        
        Args:
            query (str): The user's query about data
            context (dict, optional): Additional context for the query
            
        Returns:
            dict: The response from the CrewAI agents with image information
        """
        # Create agents
        consultant = self.create_data_consultant_agent()
        analyst = self.create_data_analyst_agent()
        
        # Create tasks
        analysis_task = self.create_task(
            agent=analyst,
            description=f"""
            Perform data analysis based on the requirements provided by the Data Consultant for this query: {query}
            
            Your responsibilities:
            1. Understand the analysis requirements from the Data Consultant
            2. Determine the appropriate analytical approach
            3. Conduct thorough data analysis
            4. Identify key patterns, trends, and insights
            5. Prepare clear visualizations and explanations of your findings using the visualization tools available to you
            6. Provide actionable recommendations based on your analysis
            
            You have access to visualization tools:
            - create_line_chart: For creating line charts with a single line
            - create_multi_line_chart: For creating line charts with multiple lines
            
            IMPORTANT: When you use these tools, they will save the chart and return an Image ID.
            You MUST include these exact Image IDs in your response exactly as returned by the tool.
            The correct format is: "Image ID: [uuid]"
            DO NOT modify this format in any way.
            DO NOT convert these Image IDs into URLs or markdown image links.
            
            Example of what you SHOULD do:
            "Here is the analysis result with a visualization. Image ID: 123e4567-e89b-12d3-a456-426614174000"
            
            Example of what you should NOT do:
            "Here is the analysis result with a visualization. ![Chart](https://example.com/image/123e4567-e89b-12d3-a456-426614174000)"
            """,
            expected_output="Detailed data analysis with visualizations, insights, and recommendations"
        )
        
        consultation_task = self.create_task(
            agent=consultant,
            description=f"""
            Review the following user query about data: {query}
            
            Your responsibilities:
            1. Understand what the user is asking for
            2. Formulate a clear analysis request for the Data Analyst
            3. Provide context and specific requirements for the analysis
            4. Review the analyst's work and ensure it addresses the user's needs
            5. Communicate the final results back to the user in a clear, business-friendly manner
            
            IMPORTANT: You should NEVER perform data analysis or create visualizations yourself.
            Always delegate these tasks to your Data Analyst team member.
            
            CRITICAL: When the Data Analyst creates visualizations, they will include Image IDs in their response.
            You MUST include these exact Image IDs in your final response without changing their format.
            The correct format is: "Image ID: [uuid]" (e.g., "Image ID: 123e4567-e89b-12d3-a456-426614174000")
            
            DO NOT convert these Image IDs into URLs or markdown image links.
            DO NOT modify the Image ID format in any way.
            DO NOT remove the "Image ID: " prefix.
            
            Example of what you SHOULD do:
            "Here is the analysis result with a visualization. Image ID: 123e4567-e89b-12d3-a456-426614174000"
            
            Example of what you should NOT do:
            "Here is the analysis result with a visualization. ![Chart](https://example.com/image/123e4567-e89b-12d3-a456-426614174000)"
            
            The system needs the exact Image ID format to properly display the images to the user.
            If you change the format, the images will not be displayed correctly.
            """,
            expected_output="A comprehensive response that addresses the user's query with insights from the data analysis"
        )
        
        # 不再設置 dependencies，因為 Task 對象沒有這個字段
        # consultation_task.dependencies = [analysis_task]
        
        try:
            print(f"Starting crew with query: {query}")
            
            # Create crew with hierarchical process
            # Set consultant as the manager and analyst as the worker
            crew = Crew(
                agents=[analyst],  # 只包含工作者代理，不包含管理者代理
                tasks=[analysis_task],  # 只包含工作者的任務，管理者的任務由 CrewAI 自動處理
                verbose=True,
                process=Process.hierarchical,  # Use hierarchical process instead of sequential
                manager_agent=consultant,  # Explicitly set consultant as the manager
                planning=True  # 啟用規劃功能，幫助管理者更好地組織任務
            )
            
            # Run the crew
            result = crew.kickoff()
            print(f"Raw result from crew: {result.raw}")
            print(f"Result type: {type(result)}")
            print(f"Result.raw type: {type(result.raw)}")
            
            # 確保 result.raw 是字符串類型
            result_text = str(result.raw) if result.raw is not None else ""
            
            # Extract image IDs from the result
            image_ids = self.extract_image_ids(result_text)
            
            # Create image info objects with full URLs
            images = []
            # 添加時間戳以防止緩存問題
            timestamp = int(time.time())
            
            for image_id in image_ids:
                images.append(
                    ImageInfo(
                        id=image_id,
                        url=f"{BASE_URL}/static/images/{image_id}.png?t={timestamp}"
                    )
                )
            
            response_data = {
                "query": query,
                "result": result_text,
                "images": images,
                "context": context
            }
            
            print(f"Returning response data: {response_data}")
            print(f"Response data keys: {response_data.keys()}")
            print(f"Response data['result'] type: {type(response_data['result'])}")
            print(f"Response data['images'] type: {type(response_data['images'])}")
            
            return response_data
        except Exception as e:
            print(f"Error in process_query_with_crew: {str(e)}")
            # 重新拋出異常，以便上層處理
            raise 