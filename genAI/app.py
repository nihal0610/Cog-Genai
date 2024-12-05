
import pandas as pd
import streamlit as st
from openai import AzureOpenAI
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain.chat_models import ChatOpenAI
from datetime import datetime

# Streamlit interface
st.title("Manager Project Analysis")

# Input for OpenAI API key
openai_api_key = st.text_input("Enter your OpenAI API key", type="password")
if not openai_api_key:
     st.error("Please enter your OpenAI API key.")
# File uploader for Excel file
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

if uploaded_file is not None and openai_api_key:
        ddf = pd.read_excel(uploaded_file)
        # Initialize the language model
        llm = ChatOpenAI(
            openai_api_key=openai_api_key,
            temperature=0,
            max_tokens=4000,
            model_name="gpt-3.5-turbo-16k"
        )
         
        # Process date columns
        ddf['ProjectEnddate2'] = pd.to_datetime(ddf['ProjectEnddate'])
        ddf['Days_Remaining'] = (ddf['ProjectEnddate2'] - datetime.now()).dt.days
        ddf['ProjectStartdate1'] = pd.to_datetime(ddf['ProjectStartdate'])
        ddf['Days_passed'] = (datetime.now() - ddf['ProjectStartdate1']).dt.days
     
        with st.sidebar:
           st.title("Please select in the drop down if u want to send project specific emails")
           a=st.selectbox('Please select one project type',('MGMNT','EXTN','SALES','PDP','INFRA','TCE','CRPIT','DMGMT','INVMT','CORP','RCMNT','BENCH','EXANT','MKTAL','OPS','CAPEX','UAMCP','ELT','GGMS','PRDCG')),
           b=st.selectbox('Please select from which Project date u want to calculate days',('Project start date','Project end date')),
           c=st.text_input("Please enter the days")
           d=st.selectbox('PLease select the days passed from the date or remaining to the date',('Passed','Remaining')),
           e=st.selectbox('PLease select either u want the results to be equal,greater or less than the amount of days u specify',('Equal to','Greater than','Less than')),
           input = f"Give me Project IDs in a list format, whose days_{d} from {b} is {e} {c} and project type is {a}"
           st.write(f"Your Query will be getting results of whose project type is {a} and days_{d} from {b} is {e} {c} days . If u wish to continue please press on submit.")
           button = st.button("Submit")
             
        if button:
             # Create the agent
             agent = create_pandas_dataframe_agent(llm, ddf, verbose=False, allow_dangerous_code=True, max_iterations=100,handle_parsing_errors=True)
          
             # Get the result
             result1 = agent.invoke(input)
             value = result1['output']   
             value = value.strip('[]').split(', ')
             value = [v.strip("'") for v in value]
             value = [int(v) for v in value]
             st.write(type(value))
             # Display the result
             st.write("Result:", value)
             # Filter DataFrame            
             df2 = ddf[ddf["Project Id"].isin(value)][["Manager ID", "Project Name", "Project Id"]]
             st.write(df2)
             df2 = pd.DataFrame()
             st.write(df2)
