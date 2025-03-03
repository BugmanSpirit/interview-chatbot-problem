import pandas as pd
import numpy as np
import json
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from enum import Enum

from google import genai
from google.genai import types

class Type(Enum):
	text = "text"
	visualization = "visualization"
	table_expr = "table_expr"

class VizType(Enum):
	bar = "bar"
	line = "line"
	scatter = "scatter"
	pie = "pie"
	histogram = "histogram"
	heatmap = "heatmap"
	box = "box"
	violin = "violin"
	area = "area"

class Viz(BaseModel):
	viz_type: VizType
	csv_file: str
	x_column: str
	y_column: str
	title: str
	colour: Optional[str]

class Expr(BaseModel):
	csv_file: str
	expr: str

class Output(BaseModel):
	response_type: Type
	answer: str
	query_expression: Optional[list[Expr]]
	visualization: Optional[Viz]

class QueryProcessor:
	def __init__(self, api_key: str):
		self.client = genai.Client(api_key = api_key)
		self.model_name = "gemini-2.0-flash"
	
	def create_system_context(self, dataframes: Dict[str, pd.DataFrame]) -> str:
		context = '''You are part of a chatbot that does Data Analysis. \
The user will provide you with some csv files and ask you a \
natural language query related to it.
The chatbot service has the ability to query the csv files (stored as \
pandas dataframes) and produce charts/graphs depicting some insights. \
To query the csv file provide an expression to be executed by the \
pandas.DataFrame.query() method in query_expression field. To produce \
graphs/charts provide the details in the visualization field.

Here is the details of the csv files that the user has uploaded:\n\n'''
		
		for name, df in dataframes.items():
			context += f"File: {name}\n"
			context += f"Columns: {', '.join(df.columns.tolist())}\n"
			context += f"Shape: {df.shape[0]} rows, {df.shape[1]} columns\n"
			
			# Add data types
			dtypes = {col: str(dtype) for col, dtype in df.dtypes.items()}
			context += f"Data types: {json.dumps(dtypes)}\n"
			
			# Add sample data (first 2 rows)
			sample = df.head(2).to_dict(orient='records')
			for record in sample:
				for key, value in record.items():
					if isinstance(value, pd.Timestamp):
						record[key] = value.strftime('%Y-%m-%d %H:%M:%S')
			context += f"Sample data: {json.dumps(sample)}\n\n"

		return context
	
	def process_query(
		self, 
		dataframes: Dict[str, pd.DataFrame], 
		query: str,
		chat_history: List[Dict[str, str]]
	) -> Dict[str, Any]:
		# Create context about the dataframes
		system_context = self.create_system_context(dataframes)
		
		# Extract recent conversation history
		chat_context = []
		for msg in chat_history:
			if msg["role"] == "user":
				chat_context.append(
					types.Content(
						parts = [types.Part.from_text(text = msg["content"])],
						role="user"
					)
				)
			elif msg["role"] == "assistant":
				chat_context.append(
					types.Content(
						parts = [types.Part.from_text(text = msg["content"])],
						role="model"
					)
				)

		response = self.client.models.generate_content(
			model = self.model_name,
			contents = chat_context,
			config = types.GenerateContentConfig(
				system_instruction = system_context,
				response_mime_type = 'application/json',
				response_schema = Output
			)
		)
		
		try:
			# Parse the JSON response
			response_text = response.text
			# Clean up the response to extract JSON
			if "```json" in response_text:
				json_str = response_text.split("```json")[1].split("```")[0].strip()
			elif "```" in response_text:
				json_str = response_text.split("```")[1].strip()
			else:
				json_str = response_text.strip()
			
			response_data = json.loads(json_str)
			return response_data
		except Exception as e:
			print(f"Error parsing AI response: {str(e)}")
			return {
				"response_type": "text",
				"answer": "I couldn't analyze the data correctly. Please try a different question or rephrase your query."
			}