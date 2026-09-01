# 📊 Autonomous Data Analyst Agent

An autonomous data analytics web application powered by *Streamlit, **Groq LLM, and a sandboxed **Python tool-calling runtime*. The agent inspects CSV datasets, automatically formulates analytical strategies, writes and executes Python/Pandas code, and generates data visualizations on the fly.

🔗 *Live Demo:* [https://autonomous-data-analyst-507.streamlit.app](https://autonomous-data-analyst-507.streamlit.app)

<img width="1881" height="989" alt="Screenshot 2026-09-01 120934" src="https://github.com/user-attachments/assets/e168c2b7-1a08-4741-a37f-baa53ce10475" />

---

## 🚀 Key Features

* *Autonomous Tool-Calling:* Inspects table schemas and iteratively runs sandboxed code to compute metrics.
* *Dynamic Chart Generation:* Automatically executes visualization scripts (Matplotlib/Seaborn) and renders charts directly into the Streamlit UI.
* *Custom & Default Datasets:* Out-of-the-box support for default sales/metrics data or user-uploaded CSV files.
* *Secure Credential Handling:* Configured with isolated secrets management (secrets.toml locally and Streamlit Cloud Secrets in production).

---

## 🛠️ Tech Stack

* *Frontend / Deployment:* Streamlit, Streamlit Community Cloud
* *LLM Engine:* Groq API (Llama 3 / Mixtral)
* *Data Manipulation & Analysis:* Python, Pandas, NumPy
* *Visualization:* Matplotlib, Seaborn

---

## 📁 Repository Structure

```text
├── .streamlit/
│   └── secrets.toml          # Local API keys (gitignored)
├── analyst_tools.py          # Execution tools for the agent
├── app.py                    # Main Streamlit application
├── company_metrics.csv       # Sample company dataset
├── requirements.txt          # Python dependencies
├── store_sales_data.csv      # Sample retail sales dataset
└── README.md                 # Project documentation
