import pandas as pd
import numpy as np
import json
from typing import Dict, List, Optional, Any

class DataManager:
	"""
	Manages the dataframes loaded from CSV files.
	Provides functionality for storage, retrieval, and basic operations.
	"""
	
	def __init__(self):
		self.dataframes: Dict[str, pd.DataFrame] = {}
		self.metadata: Dict[str, Dict[str, Any]] = {}
	
	def add_dataframe(self, name: str, df: pd.DataFrame) -> bool:
		try:
			self.dataframes[name] = df
			
			# Generate and store metadata
			self.metadata[name] = {
				"shape": df.shape,
				"columns": df.columns.tolist(),
				"dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
				"numeric_columns": df.select_dtypes(include=[np.number]).columns.tolist(),
				"categorical_columns": df.select_dtypes(include=["object", "category"]).columns.tolist(),
				"datetime_columns": df.select_dtypes(include=["datetime"]).columns.tolist(),
				"missing_values": df.isna().sum().to_dict()
			}
			return True
		except Exception as e:
			print(f"Error adding dataframe: {str(e)}")
			return False
	
	def get_dataframe(self, name: str) -> Optional[pd.DataFrame]:
		return self.dataframes.get(name)
	
	def get_all_dataframes(self) -> Dict[str, pd.DataFrame]:
		return self.dataframes
	
	def get_dataframe_names(self) -> List[str]:
		return list(self.dataframes.keys())
	
	def get_metadata(self, name: Optional[str] = None) -> Dict:
		if name:
			return self.metadata.get(name, {})
		return self.metadata
	
	def clear_dataframes(self) -> None:
		self.dataframes = {}
		self.metadata = {}
	
	def execute_query(self, name: str, query: str) -> Optional[pd.DataFrame]:
		try:
			df = self.get_dataframe(name)
			if df:
				return df.query(query)
			return None
		except Exception as e:
			print(f"Error executing query: {str(e)}")
			return None