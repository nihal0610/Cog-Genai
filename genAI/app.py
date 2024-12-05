
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

# File uploader for Excel file
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx", "csv"])

# Input for prompt
prompt = st.text_area("Enter your prompt")

if st.button("Submit"):
     
    with st.sidebar:
           st.title("Please select in the drop down if u want to send project specific emails")
           a=st.selectbox('Please select one project type',('MGMNT','EXTN','SALES','PDP','INFRA','TCE','CRPIT','DMGMT','INVMT','CORP','RCMNT','BENCH','EXANT','MKTAL','OPS','CAPEX','UAMCP','ELT','GGMS','PRDCG')),
           b=st.selectbox('Please select from which Project date u want to calculate days',('Project start date','Project end date')),
           c=st.text_input("Please enter the days")
           e=st.selectbox('PLease select the days passed from the date or remaining to the date',('Passed','Remaining')),
           d=st.selectbox('PLease select either u want the results to be equal,greater or less than the amount of days u specify',('Equal to','Greater than','Less than')),
           st.write(f"Your Query will be Sending mails to all manger under project type {a} who has {d} {c} days {e} from {b}. If u wish to continue please press on submit.")
            
    if not openai_api_key:
        st.error("Please enter your OpenAI API key.")
    elif not uploaded_file:
        st.error("Please upload an Excel file.")
    elif not prompt:
        st.error("Please enter a prompt.")
    else:
        # Read the uploaded file
        if uploaded_file.name.endswith('.csv'):
            ddf = pd.read_csv(uploaded_file)
        else:
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

       
       

        # Create the agent
        agent = create_pandas_dataframe_agent(llm, ddf, verbose=False, allow_dangerous_code=True, full_output=False, max_iterations=100)

        # Get the result
        result1 = agent.invoke(prompt)
        value = result1['output']

        if isinstance(value, str):
            value = value.strip('[]').split(', ')
            value = [v.strip("'") for v in value]
            #value = [int(v) for v in value]

        # Display the result
        st.write("Result:", value)

        # Filter DataFrame
        filtered_df = ddf[ddf["Manager ID"].isin(value)][["Manager ID", "Project Name", "Project Id"]]
        st.write(filtered_df)

        # Save to Excel
        filtered_df.to_excel('outputttt.xlsx', index=False)
        st.success("Filtered data saved to outputttt.xlsx")



