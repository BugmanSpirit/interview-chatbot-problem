import pandas as pd
import numpy as np

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
	"""
	Clean a pandas DataFrame by handling missing values,
	converting data types, and basic preprocessing.
	"""
	cleaned_df = df.copy()
	
	# Handle missing values
	for col in cleaned_df.columns:
		dtype = cleaned_df[col].dtype
		
		# For numeric columns
		if pd.api.types.is_numeric_dtype(dtype):
			cleaned_df[col] = cleaned_df[col].fillna(cleaned_df[col].median())
		else:
			# Fill with mode for categorical columns
			mode_value = cleaned_df[col].mode()
			if not mode_value.empty:
				cleaned_df[col] = cleaned_df[col].fillna(mode_value[0])
			else:
				# If no mode, fill with 'Unknown'
				cleaned_df[col] = cleaned_df[col].fillna('Unknown')
	
	# Convert date columns
	for col in cleaned_df.columns:
		# Check if column name suggests a date
		if any(date_hint in col.lower() for date_hint in ['date', 'time', 'year', 'month', 'day']):
			try:
				cleaned_df[col] = pd.to_datetime(cleaned_df[col], errors='coerce')
				# Fill any failed conversions (NaT) with the min date in the column
				min_date = cleaned_df[col].min()
				cleaned_df[col] = cleaned_df[col].fillna(min_date)
			except:
				pass
	
	# Convert numeric columns
	for col in cleaned_df.columns:
		if cleaned_df[col].dtype == 'object':
			try:
				# Check if column contains numbers stored as strings
				if cleaned_df[col].str.match(r'^-?\d+\.?\d*$').all(skipna=True):
					cleaned_df[col] = pd.to_numeric(cleaned_df[col], errors='coerce')
			except:
				pass

	return cleaned_df