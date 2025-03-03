import streamlit as st
import pandas as pd
import json
import os
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go

from backend.data_manager import DataManager
from backend.query_processor import QueryProcessor
from backend.visualization import Visualizer
from utils.data_cleaning import clean_dataframe

# Initialize session state variables
if "messages" not in st.session_state:
	st.session_state["messages"] = [{"role": "assistant", "content": "Upload your CSV files in the sidebar, then ask questions about the data."}]

if "data_manager" not in st.session_state:
	st.session_state["data_manager"] = DataManager()

if "visualizer" not in st.session_state:
	st.session_state["visualizer"] = Visualizer()

# Sidebar
with st.sidebar:
	st.title("CSV Data Analysis")
	api_key = st.text_input("Gemini API Key", key="gemini_api_key", type="password")
	"[Get a Gemini API key](https://aistudio.google.com/app/apikey)"
	
	uploaded_files = st.file_uploader(
		"Upload CSV files", 
		type=["csv"], 
		accept_multiple_files=True
	)
	
	# Process uploaded files
	if uploaded_files:
		data_manager = st.session_state["data_manager"]
		
		# Clear existing dataframes if new files are uploaded
		if not st.session_state.get("files_processed"):
			data_manager.clear_dataframes()
			st.session_state["files_processed"] = True
			
		file_info = []
		for file in uploaded_files:
			if file.name not in data_manager.get_dataframe_names():
				try:
					df = pd.read_csv(file)
					cleaned_df = clean_dataframe(df)
					
					data_manager.add_dataframe(file.name, cleaned_df)
					
					file_info.append({
						"name": file.name,
						"rows": df.shape[0],
						"columns": df.shape[1]
					})
				except Exception as e:
					st.error(f"Error processing {file.name}: {str(e)}")
		
		if file_info:
			st.write(f"📂 {len(data_manager.get_dataframe_names())} files uploaded:")
			for info in file_info:
				st.write(f"- {info['name']} ({info['rows']} rows, {info['columns']} columns)")

# Main app area
st.title("💬 CSV Data Analysis Chatbot")
st.caption("Chat-Based Data Analysis on Multiple CSVs")

if st.session_state["data_manager"].get_dataframe_names():
	with st.expander("Preview Data", expanded=False):
		dfs = st.session_state["data_manager"].get_all_dataframes()
		selected_df = st.selectbox("Select file to preview:", list(dfs.keys()))
		st.dataframe(dfs[selected_df].head(5), use_container_width=True)

for msg in st.session_state.messages:
	st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("Ask a question about your data..."):
	# Check if API key is provided
	if not api_key:
		st.info("Please add your API key to continue.")
		st.stop()
	
	# Check if files are uploaded
	data_manager = st.session_state["data_manager"]
	if not data_manager.get_dataframe_names():
		st.error("Please upload at least one CSV file first.")
		st.chat_message("user").write(prompt)
		st.chat_message("assistant").write("I need some CSV files to analyze. Please upload them in the sidebar.")
		st.stop()
	
	st.session_state.messages.append({"role": "user", "content": prompt})
	st.chat_message("user").write(prompt)
	
	query_processor = QueryProcessor(api_key)
	
	# Process query
	with st.spinner("Analyzing your data..."):
		try:
			dataframes = data_manager.get_all_dataframes()
			
			response_data = query_processor.process_query(
				dataframes, 
				prompt, 
				st.session_state["messages"]
			)

			# Display text response
			st.session_state.messages.append({"role": "assistant", "content": response_data["answer"]})
			st.chat_message("assistant").write(response_data["answer"])
				
			# Handle visualiation/table expressions
			if response_data["response_type"] == "visualization":
				visualizer = st.session_state["visualizer"]
				fig = visualizer.create_visualization(dataframes, response_data["visualization"])
				st.plotly_chart(fig, use_container_width=True)
			
			elif response_data["response_type"] == "table_expr":
				with st.expander("Results", expanded = True):
					expr_responses = {resp["csv_file"]: resp["expr"] for resp in response_data["query_expression"]}
					selected_df = st.selectbox("Select dataframe to view:", list(expr_responses.keys()))
					st.dataframe(dataframes[selected_df].query(expr_responses[selected_df]).head(10), use_container_width=True)
						
		except Exception as e:
			error_msg = f"Error processing your request: {str(e)}"
			st.session_state.messages.append({"role": "assistant", "content": error_msg})
			st.chat_message("assistant").write(error_msg)