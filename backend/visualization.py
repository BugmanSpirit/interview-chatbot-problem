import pandas as pd
import numpy as np
import json
from typing import Dict, List, Optional, Any
import plotly.express as px
import plotly.graph_objects as go

class Visualizer:
	def __init__(self):
		self.chart_types = {
			"bar": self._create_bar_chart,
			"line": self._create_line_chart,
			"scatter": self._create_scatter_chart,
			"pie": self._create_pie_chart
		}
	
	def create_visualization(
		self, 
		dataframes: Dict[str, pd.DataFrame], 
		viz_config: Dict[str, Any]
	) -> Optional[go.Figure]:
		try:
			chart_type = viz_config.get('viz_type', '').lower()
			file_name = viz_config.get('csv_file', '')

			if file_name not in dataframes:
				return None
			
			df = dataframes[file_name]

			if chart_type in self.chart_types:
				return self.chart_types[chart_type](df, viz_config)
			else:
				return self._create_bar_chart(df, viz_config)
			
		except Exception as e:
			print(f"Error creating visualization: {str(e)}")
			return None
	
	def _create_bar_chart(self, df: pd.DataFrame, config: Dict[str, Any]) -> go.Figure:
		x_col = config.get('x_column')
		y_col = config.get('y_column')
		title = config.get('title', 'Bar Chart')
		color = config.get('color')
		
		if color:
			fig = px.bar(df, x=x_col, y=y_col, color=color, title=title)
		else:
			fig = px.bar(df, x=x_col, y=y_col, title=title)

		fig.update_layout(
			xaxis_title=x_col,
			yaxis_title=y_col,
			legend_title_text=color if color else None,
			height=500
		)
		
		return fig
	
	def _create_line_chart(self, df: pd.DataFrame, config: Dict[str, Any]) -> go.Figure:
		"""Create a line chart."""
		x_col = config.get('x_column')
		y_col = config.get('y_column')
		title = config.get('title', 'Line Chart')
		color = config.get('color')
		
		if color:
			fig = px.line(df, x=x_col, y=y_col, color=color, title=title)
		else:
			fig = px.line(df, x=x_col, y=y_col, title=title)

		fig.update_layout(
			xaxis_title=x_col,
			yaxis_title=y_col,
			legend_title_text=color if color else None,
			height=500
		)
		
		return fig
	
	def _create_scatter_chart(self, df: pd.DataFrame, config: Dict[str, Any]) -> go.Figure:
		"""Create a scatter plot."""
		x_col = config.get('x_column')
		y_col = config.get('y_column')
		title = config.get('title', 'Scatter Plot')
		color = config.get('color')
		size = config.get('size')
		
		if color and size:
			fig = px.scatter(df, x=x_col, y=y_col, color=color, size=size, title=title)
		elif color:
			fig = px.scatter(df, x=x_col, y=y_col, color=color, title=title)
		else:
			fig = px.scatter(df, x=x_col, y=y_col, title=title)

		fig.update_layout(
			xaxis_title=x_col,
			yaxis_title=y_col,
			legend_title_text=color if color else None,
			height=500
		)
		
		return fig
	
	def _create_pie_chart(self, df: pd.DataFrame, config: Dict[str, Any]) -> go.Figure:
		"""Create a pie chart."""
		names = config.get('x_column')  # Categories
		values = config.get('y_column')  # Values
		title = config.get('title', 'Pie Chart')
		
		fig = px.pie(df, names=names, values=values, title=title)

		fig.update_layout(
			height=500
		)
		
		return fig