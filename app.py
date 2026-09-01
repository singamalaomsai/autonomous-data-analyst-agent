import io
import json
import os
import sys
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from groq import Groq

# ---------------------------------------------------------
# 1. Page Configuration & Setup
# ---------------------------------------------------------
st.set_page_config(
    page_title="Autonomous Data Analyst Agent",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Autonomous Data Analyst Agent")
st.caption("Powered by Groq LLMs, Pandas, & Tool-Calling Runtime Execution")

# ---------------------------------------------------------
# 2. Sidebar Configuration & Dataset Loader
# ---------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Configuration")
    # Check secrets or prompt user
    default_key = ""
    try:
        default_key = st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        pass

    api_key_input = st.text_input(
        "Groq API Key", 
        type="password", 
        value=default_key,
        placeholder="Enter your Groq API Key (gsk_...)"
    )
    
    st.divider()
    st.header("📁 Data Source")
    uploaded_file = st.file_uploader("Upload CSV Dataset", type=["csv"])
    
    # Load default data if no file is uploaded
    if uploaded_file is not None:
        st.session_state.df = pd.read_csv(uploaded_file)
        st.success(f"Loaded {uploaded_file.name} ({len(st.session_state.df)} rows)")
    elif "df" not in st.session_state:
        if os.path.exists("company_metrics.csv"):
            st.session_state.df = pd.read_csv("company_metrics.csv")
            st.info(f"Loaded default company_metrics.csv ({len(st.session_state.df)} rows)")
        else:
            st.warning("Please upload a CSV file to proceed.")

    if st.button("Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.session_state.groq_messages = []
        st.rerun()

# ---------------------------------------------------------
# 3. Dynamic Tool Definition for Active Session
# ---------------------------------------------------------
def inspect_dataset_tool():
    if "df" not in st.session_state or st.session_state.df is None:
        return "Error: No dataset currently loaded."
    
    df = st.session_state.df
    buffer = io.StringIO()
    df.info(buf=buffer)
    info_str = buffer.getvalue()
    
    summary = f"""Dataset Overview:
Total Rows: {len(df)}, Total Columns: {len(df.columns)}

Column Names & Types:
{info_str}

First 3 Rows (Sample):
{df.head(3).to_string()}
"""
    return summary

def execute_python_analysis_tool(code: str):
    if "df" not in st.session_state or st.session_state.df is None:
        return "Error: No dataset loaded in memory."
    
    df = st.session_state.df
    plt.close("all")
    
    # Capture stdout
    stdout_capture = io.StringIO()
    sys_stdout_backup = sys.stdout
    sys.stdout = stdout_capture
    
    execution_context = {
        "df": df,
        "pd": pd,
        "plt": plt
    }
    
    chart_generated = False
    try:
        exec(code, execution_context)
        
        # Check if a plot was constructed
        if plt.get_fignums():
            plt.savefig("output_chart.png", bbox_inches="tight", dpi=150)
            chart_generated = True
            plt.close("all")
            
        sys.stdout = sys_stdout_backup
        output = stdout_capture.getvalue().strip()
        
        if chart_generated:
            output += "\n[System Notice]: Chart successfully rendered and saved to 'output_chart.png'."
        if not output:
            output = "[Success]: Code executed with no terminal text output."
            
        return output, chart_generated
    except Exception as e:
        sys.stdout = sys_stdout_backup
        return f"Execution Error: {str(e)}", False

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "inspect_dataset",
            "description": "Inspect the columns, data types, and first few rows of the active dataset.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "execute_python_analysis",
            "description": "Execute Python/Pandas code to aggregate data or plot with matplotlib (saved automatically as 'output_chart.png'). Active dataset is available as df.",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Executable Python code block. Must use print() to output results."
                    }
                },
                "required": ["code"]
            }
        }
    }
]

SYSTEM_PROMPT = """You are an Autonomous Data Analyst Agent.
Your objective is to answer business questions accurately using data analysis and visualizations.

Workflow Rules:
1. Always inspect the dataset first using inspect_dataset if you don't know the exact column names.
2. Formulate and execute clean Python code using execute_python_analysis.
3. If an execution returns an error, inspect the traceback, fix the code, and re-run.
4. When asked for charts, write matplotlib/seaborn code using plt.
5. Provide a clear, structured executive summary answering the business question directly.
"""

# ---------------------------------------------------------
# 4. Initialize State
# ---------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []  # UI rendering list: list of dicts {"role": ..., "content": ..., "code": ..., "image": ...}

if "groq_messages" not in st.session_state:
    st.session_state.groq_messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

# Render previous chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("code"):
            with st.expander("🛠️ View Generated Python Code"):
                st.code(msg["code"], language="python")
        if msg.get("image") and os.path.exists(msg["image"]):
            st.image(msg["image"], caption="Generated Visualization")

# ---------------------------------------------------------
# 5. Handle User Query & Agent Execution Loop
# ---------------------------------------------------------
user_prompt = st.chat_input("Ask a question about the dataset...")

if user_prompt:
    if not api_key_input or "gsk_" not in api_key_input:
        st.error("Please provide a valid Groq API key in the sidebar.")
        st.stop()

    client = Groq(api_key=api_key_input)
    
    # Render user prompt
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    st.session_state.groq_messages.append({"role": "user", "content": user_prompt})
    
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # Run Agent ReAct loop
    with st.chat_message("assistant"):
        status_box = st.status("🧠 Agent is analyzing data...", expanded=True)
        
        last_generated_code = None
        has_new_chart = False
        final_summary = ""
        
        max_turns = 8
        for turn in range(max_turns):
            response = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=st.session_state.groq_messages,
                tools=TOOLS,
                tool_choice="auto"
            )
            
            choice = response.choices[0].message
            st.session_state.groq_messages.append(choice)

            # If no tool calls, the model provided its final synthesis
            if not choice.tool_calls:
                final_summary = choice.content
                status_box.update(label="✅ Analysis Complete!", state="complete", expanded=False)
                break
            
            # Process tool calls
            for tool_call in choice.tool_calls:
                fn_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                
                if fn_name == "inspect_dataset":
                    status_box.write("🔍 Inspecting dataset structure & sample rows...")
                    observation = inspect_dataset_tool()
                elif fn_name == "execute_python_analysis":
                    last_generated_code = args.get("code", "")
                    status_box.write("💻 Executing Python code for analysis/plotting...")
                    status_box.code(last_generated_code, language="python")
                    observation, chart_flag = execute_python_analysis_tool(last_generated_code)
                    if chart_flag:
                        has_new_chart = True
                else:
                    observation = f"Error: Unknown tool {fn_name}"

                # Append tool observation back to Groq message history
                st.session_state.groq_messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": observation
                })

        # Display Final Summary & Visuals
        st.markdown(final_summary)
        
        chart_path = None
        if has_new_chart and os.path.exists("output_chart.png"):
            chart_path = "output_chart.png"
            st.image(chart_path, caption="Generated Visualization")

        # Save assistant message to persistent UI state
        st.session_state.messages.append({
            "role": "assistant",
            "content": final_summary,
            "code": last_generated_code,
            "image": chart_path
        })