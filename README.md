# Chat-Based Data Analysis on Multiple CSVs

## How the system works
User can input multiple messages regarding a query and input csvs. Assistant can respond in 3 modes: text, visualization and tables. Gemini's api is used to get response in structured output format. Assistant can return response in tables mode with an expression for `pd.Dataframe.query()` or it can return details required to build a chart/graph using `plotly` in visualization mode.

## How to set up and run the project
```
cd interview-chatbot-problem
python -m venv .deploy
source .deploy/bin/activate
pip install -r requirments.txt
streamlit run frontend.py
```
## Libraries used and why
| Libraries | Why |
| --- | --- |
|`pandas`, `numpy` | Dataframe management, cleaning, analysis |
|`plotly` | Generate charts |
|`streamlit` | Frontend |
|`google-genai` | Communicating with Gemini |

## How evaluation could be performed
Write integration and Regression tests for:
- Testing functionality with improper csvs: null values, incorrect dtypes, different formatting for datetime
- Introduce SQL in output and check against output's response with desired sql qury.