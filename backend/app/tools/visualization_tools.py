"""
Visualization tools for data analysis.
"""

import json
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import base64
import os
import uuid
from io import BytesIO
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union, Type

# Define a constant for the image storage directory
IMAGE_STORAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "images")
# Ensure the directory exists
os.makedirs(IMAGE_STORAGE_DIR, exist_ok=True)

class LineChartInput(BaseModel):
    """Input schema for LineChartTool."""
    x_data: Union[List[str], List[int], List[float]] = Field(
        ..., 
        description="List of values for the x-axis (can be strings, integers, or floats)"
    )
    y_data: Union[List[int], List[float]] = Field(
        ..., 
        description="List of values for the y-axis (must be integers or floats)"
    )
    title: str = Field(
        default="Line Chart", 
        description="Title of the chart"
    )
    x_label: str = Field(
        default="X Axis", 
        description="Label for the x-axis"
    )
    y_label: str = Field(
        default="Y Axis", 
        description="Label for the y-axis"
    )
    color: str = Field(
        default="blue", 
        description="Color of the line (e.g., 'blue', 'red', 'green', etc.)"
    )
    line_width: int = Field(
        default=2, 
        description="Width of the line"
    )
    markers: bool = Field(
        default=True, 
        description="Whether to include markers on the line"
    )
    include_data_table: bool = Field(
        default=False, 
        description="Whether to include a data table below the chart"
    )

class LineChartTool(BaseTool):
    """Tool for creating line chart visualizations."""
    name: str = "create_line_chart"
    description: str = "Create a line chart visualization using Matplotlib. Useful for visualizing trends over time or comparing values across categories."
    args_schema: Type[BaseModel] = LineChartInput

    def _run(
        self, 
        x_data: Union[List[str], List[int], List[float]],
        y_data: Union[List[int], List[float]],
        title: str = "Line Chart",
        x_label: str = "X Axis",
        y_label: str = "Y Axis",
        color: str = "blue",
        line_width: int = 2,
        markers: bool = True,
        include_data_table: bool = False
    ) -> str:
        """
        Create a line chart visualization using Matplotlib.
        
        Args:
            x_data: List of values for the x-axis (can be strings, integers, or floats)
            y_data: List of values for the y-axis (must be integers or floats)
            title: Title of the chart
            x_label: Label for the x-axis
            y_label: Label for the y-axis
            color: Color of the line (e.g., 'blue', 'red', 'green', etc.)
            line_width: Width of the line
            markers: Whether to include markers on the line
            include_data_table: Whether to include a data table below the chart
            
        Returns:
            A string with the image ID and a reference to access it
        """
        try:
            # Create a DataFrame from the data
            df = pd.DataFrame({x_label: x_data, y_label: y_data})
            
            # Create the figure
            if include_data_table:
                # Create a figure with two subplots (chart and table)
                fig, (ax_chart, ax_table) = plt.subplots(2, 1, figsize=(10, 12), 
                                                         gridspec_kw={'height_ratios': [3, 1]})
                
                # Plot the line chart on the first subplot
                if markers:
                    ax_chart.plot(df[x_label], df[y_label], color=color, linewidth=line_width, marker='o')
                else:
                    ax_chart.plot(df[x_label], df[y_label], color=color, linewidth=line_width)
                
                ax_chart.set_title(title)
                ax_chart.set_xlabel(x_label)
                ax_chart.set_ylabel(y_label)
                ax_chart.grid(True, linestyle='--', alpha=0.7)
                
                # Create a table on the second subplot
                table_data = [df[x_label].tolist(), df[y_label].tolist()]
                table_cols = [x_label, y_label]
                
                # Hide the axes for the table subplot
                ax_table.axis('tight')
                ax_table.axis('off')
                
                # Create the table
                table = ax_table.table(cellText=list(map(list, zip(*table_data))),
                                      colLabels=table_cols,
                                      loc='center',
                                      cellLoc='center')
                
                # Style the table
                table.auto_set_font_size(False)
                table.set_fontsize(10)
                table.scale(1, 1.5)
                
                ax_table.set_title("Data Table")
                
            else:
                # Create a simple figure with just the chart
                fig, ax = plt.subplots(figsize=(10, 6))
                
                # Plot the line chart
                if markers:
                    ax.plot(df[x_label], df[y_label], color=color, linewidth=line_width, marker='o')
                else:
                    ax.plot(df[x_label], df[y_label], color=color, linewidth=line_width)
                
                ax.set_title(title)
                ax.set_xlabel(x_label)
                ax.set_ylabel(y_label)
                ax.grid(True, linestyle='--', alpha=0.7)
            
            # Adjust layout
            plt.tight_layout()
            
            # Generate a unique ID for the image
            image_id = str(uuid.uuid4())
            image_filename = f"{image_id}.png"
            image_path = os.path.join(IMAGE_STORAGE_DIR, image_filename)
            
            # Save the figure to the file system
            plt.savefig(image_path, format='png', dpi=100)
            
            # Close the figure to free memory
            plt.close(fig)
            
            # Return a reference to the image that can be used by the frontend
            return f"I have created a {title} visualization. Image ID: {image_id}\n\nDo not modify this Image ID as it is needed to display the chart correctly."
        
        except Exception as e:
            return f"Error creating line chart: {str(e)}"

class MultiLineChartInput(BaseModel):
    """Input schema for MultiLineChartTool."""
    data: List[Dict[str, Any]] = Field(
        ..., 
        description="List of dictionaries containing the data"
    )
    x_key: str = Field(
        ..., 
        description="Key in the dictionaries for x-axis values"
    )
    y_keys: List[str] = Field(
        ..., 
        description="List of keys in the dictionaries for y-axis values (multiple lines)"
    )
    title: str = Field(
        default="Multi-Line Chart", 
        description="Title of the chart"
    )
    x_label: str = Field(
        default="X Axis", 
        description="Label for the x-axis"
    )
    y_label: str = Field(
        default="Y Axis", 
        description="Label for the y-axis"
    )
    colors: Optional[List[str]] = Field(
        default=None, 
        description="List of colors for each line (if None, default colors will be used)"
    )
    line_width: int = Field(
        default=2, 
        description="Width of the lines"
    )
    markers: bool = Field(
        default=True, 
        description="Whether to include markers on the lines"
    )

class MultiLineChartTool(BaseTool):
    """Tool for creating multi-line chart visualizations."""
    name: str = "create_multi_line_chart"
    description: str = "Create a multi-line chart visualization using Matplotlib. Useful for comparing multiple data series over time or across categories."
    args_schema: Type[BaseModel] = MultiLineChartInput

    def _run(
        self,
        data: List[Dict[str, Any]],
        x_key: str,
        y_keys: List[str],
        title: str = "Multi-Line Chart",
        x_label: str = "X Axis",
        y_label: str = "Y Axis",
        colors: Optional[List[str]] = None,
        line_width: int = 2,
        markers: bool = True
    ) -> str:
        """
        Create a multi-line chart visualization using Matplotlib.
        
        Args:
            data: List of dictionaries containing the data
            x_key: Key in the dictionaries for x-axis values
            y_keys: List of keys in the dictionaries for y-axis values (multiple lines)
            title: Title of the chart
            x_label: Label for the x-axis
            y_label: Label for the y-axis
            colors: List of colors for each line (if None, default colors will be used)
            line_width: Width of the lines
            markers: Whether to include markers on the lines
            
        Returns:
            A string with the image ID and a reference to access it
        """
        try:
            # Create a DataFrame from the data
            df = pd.DataFrame(data)
            
            # Create the figure
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Plot each line
            for i, y_key in enumerate(y_keys):
                color = colors[i] if colors and i < len(colors) else None
                if markers:
                    ax.plot(df[x_key], df[y_key], label=y_key, linewidth=line_width, marker='o', color=color)
                else:
                    ax.plot(df[x_key], df[y_key], label=y_key, linewidth=line_width, color=color)
            
            # Add legend, title, and labels
            ax.legend()
            ax.set_title(title)
            ax.set_xlabel(x_label)
            ax.set_ylabel(y_label)
            ax.grid(True, linestyle='--', alpha=0.7)
            
            # Adjust layout
            plt.tight_layout()
            
            # Generate a unique ID for the image
            image_id = str(uuid.uuid4())
            image_filename = f"{image_id}.png"
            image_path = os.path.join(IMAGE_STORAGE_DIR, image_filename)
            
            # Save the figure to the file system
            plt.savefig(image_path, format='png', dpi=100)
            
            # Close the figure to free memory
            plt.close(fig)
            
            # Return a reference to the image that can be used by the frontend
            return f"I have created a {title} visualization with multiple lines. Image ID: {image_id}\n\nDo not modify this Image ID as it is needed to display the chart correctly."
        
        except Exception as e:
            return f"Error creating multi-line chart: {str(e)}"

# Create instances of the tools
create_line_chart = LineChartTool()
create_multi_line_chart = MultiLineChartTool() 