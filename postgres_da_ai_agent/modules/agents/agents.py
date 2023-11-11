import os
import dotenv
from autogen import (
    AssistantAgent,
    UserProxyAgent,
)
from postgres_da_ai_agent.modules.file.file import write_file
from postgres_da_ai_agent.modules.config.config import gpt4_config, write_file_config
from postgres_da_ai_agent.modules.utils.utils import in_termination_msg
from postgres_da_ai_agent.modules.prompts.prompts import (
    USER_PROXY_PROMPT,
    DATA_ENGINEER_PROMPT,
    DATA_ANALYST_PROMPT,
    PRODUCT_MANAGER_PROMPT,
    TEXT_REPORT_ANALYSIS_PROMPT
)
from postgres_da_ai_agent.modules.db.db import PostgresDB

dotenv.load_dotenv()

assert os.environ.get(
    "DATABASE_URL"), "POSTGRES_CONNECTION_URL not found in .env file"

DB_URL = os.environ.get("DATABASE_URL")

db = PostgresDB()
db.connect_with_url(DB_URL)

function_map = {
    "run_sql": db.run_sql
}

write_file_function_map = {
    "write_file": write_file
}

admin_user_proxy_agent = UserProxyAgent(
    name="Admin",
    system_message=USER_PROXY_PROMPT,
    code_execution_config=False,
    human_input_mode="NEVER",
    is_termination_msg=in_termination_msg,
)

data_engineer_agent = AssistantAgent(
    name="Data_Engineer",
    llm_config=gpt4_config,
    system_message=DATA_ENGINEER_PROMPT,
    code_execution_config=False,
    human_input_mode="NEVER",
    is_termination_msg=in_termination_msg,
)

sr_data_analyst_agent = AssistantAgent(
    name="Sr_Data_Analyst",
    llm_config=gpt4_config,
    system_message=DATA_ANALYST_PROMPT,
    human_input_mode="NEVER",
    code_execution_config=False,
    is_termination_msg=in_termination_msg,
    function_map=function_map,
)

product_manager_agent = AssistantAgent(
    name="Product_Manager",
    llm_config=gpt4_config,
    system_message=PRODUCT_MANAGER_PROMPT,
    human_input_mode="NEVER",
    code_execution_config=False,
    is_termination_msg=in_termination_msg,
)

text_report_agent = AssistantAgent(
    name="Text_Report_Analyst",
    llm_config=write_file_config,
    system_message=TEXT_REPORT_ANALYSIS_PROMPT,
    human_input_mode="NEVER",
    function_map=write_file_function_map
)
