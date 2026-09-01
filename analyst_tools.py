import io
import sys
import traceback
import pandas as pd
import matplotlib.pyplot as plt

DATA_FILE = "company_metrics.csv"

def inspect_dataset() -> str:
    """Returns the schema, column types, and first few rows of the dataset."""
    try:
        df = pd.read_csv(DATA_FILE)
        buffer = io.StringIO()
        buffer.write("Dataset Overview:\n")
        buffer.write(f"Total Rows: {len(df)}, Total Columns: {len(df.columns)}\n\n")
        buffer.write("Column Names & Types:\n")
        df.info(buf=buffer)
        buffer.write("\nFirst 3 Sample Rows:\n")
        buffer.write(df.head(3).to_string())
        return buffer.getvalue()
    except Exception as e:
        return f"Error reading dataset: {str(e)}"

def execute_python_analysis(code: str) -> str:
    """
    Executes generated Python code on the dataset.
    The DataFrame is pre-loaded as df.
    Captures console stdout, errors, and exports matplotlib plots to 'output_chart.png'.
    """
    try:
        df = pd.read_csv(DATA_FILE)
    except Exception as e:
        return f"Failed to load dataset: {str(e)}"

    old_stdout = sys.stdout
    redirected_output = io.StringIO()
    sys.stdout = redirected_output

    local_env = {
        "pd": pd,
        "df": df,
        "plt": plt,
    }

    error_output = None
    try:
        plt.clf()
        exec(code, {}, local_env)
        
        if plt.get_fignums():
            plt.savefig("output_chart.png", bbox_inches="tight")
            plt.close()
            redirected_output.write("\n[Artifact Saved: 'output_chart.png']")
    except Exception:
        error_output = traceback.format_exc()
    finally:
        sys.stdout = old_stdout

    if error_output:
        return f"Execution Error:\n{error_output}"
    
    result = redirected_output.getvalue().strip()
    return result if result else "Code executed successfully with no textual output."

if __name__ == "_main_":
    print("--- 1. Testing inspect_dataset() ---")
    print(inspect_dataset())

    print("\n--- 2. Testing execute_python_analysis() ---")
    test_script = """
mean_spend = df.groupby('segment')['monthly_spend'].mean()
print("Average spend per segment:")
print(mean_spend)
"""
    print(execute_python_analysis(test_script))