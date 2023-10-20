import os
import dotenv
import argparse
from postgres_da_ai_agent.modules.db import PostgresDB
from postgres_da_ai_agent.modules import llm
from autogen import (
    AssistantAgent,
    UserProxyAgent,
    GroupChat,
    GroupChatManager,
    config_list_from_json,
    config_list_from_models,
)

dotenv.load_dotenv()

assert os.environ.get(
    "DATABASE_URL"), "POSTGRES_CONNECTION_URL not found in .env file"
assert os.environ.get(
    "OPENAI_API_KEY"), "OPENAI_API_KEY not found in .env file"

DB_URL = os.environ.get("DATABASE_URL")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

POSTGRES_TABLE_DEFINITIONS_CAP_REF = "TABLE_DEFINITIONS"
TABLE_RESPONSE_FORMAT_CAP_REF = "TABLE_RESPONSE_FORMAT"

SQL_QUERY_DELIMITER = '-----------'
AGENT_RESULT_DELIMITER = '-------- AGENT RESULT --------'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", help="The prompt for the AI model")
    args = parser.parse_args()

    db = PostgresDB()
    db.connect_with_url(DB_URL)
    table_definitions = db.get_table_definitions_for_prompt()

    prompt = args.prompt

    prompt = llm.add_cap_ref(
        prompt,
        f"Use this {POSTGRES_TABLE_DEFINITIONS_CAP_REF} to satisfy the database query.",
        POSTGRES_TABLE_DEFINITIONS_CAP_REF,
        table_definitions,
    )

    gpt4_config = {
        "use_cache": False,
        "temperature": 0,
        "config_list": config_list_from_models(["gpt-4"]),
        "request_timeout": 120,
        "functions": [
            {
                "name": "run_sql",
                "description": "Run the SQL query agains the DB",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "sql": {
                            "type": "string",
                            "description": "SQL query to run against the DB",
                        },
                    },
                    "required": ["sql"],
                }
            }
        ]
    }

    function_map = {
        "run_sql": db.run_sql
    }

    def in_termination_msg(content):
        have_content = content.get("content", None) is not None
        if have_content and "APPROVED" in content["content"]:
            return True
        return False

    COMPLETION_PROMPT = "If everything looks good overall, respond with the word APPROVED"
    USER_PROXY_PROMPT = (
        "A human admin. Interact with the planner to discuss the plan. Plan execution needs to be approved by this admin." + COMPLETION_PROMPT
    )
    DATA_ENGINEER_PROMPT = (
        f'''A Data Engineer. You follow an approved plan. You write python/shell code to solve tasks. Wrap the code in a code block that specifies the script type. The user can't modify your code. So do not suggest incomplete code which requires others to modify. Don't use a code block if it's not intended to be executed by the executor.
            Don't include multiple code blocks in one response. Do not ask others to copy and paste the result. Check the execution result returned by the executor.
            If the result indicates there is an error, fix the error and output the code again. Suggest the full code instead of partial code or code changes. If the error can't be fixed or if the task is not solved even after the code is executed successfully, analyze the problem, revisit your assumption, collect additional info you need, and think of a different approach to try.
            {COMPLETION_PROMPT}
        '''
    )
    DATA_ANALYST_PROMPT = (
        "A Sr Data Analyst. You follow an approved plan. You run the sql query, generate the response and send it to the product manager for final review." + COMPLETION_PROMPT
    )

    PRODUCT_MANAGER_PROMPT = (
        "A Product Manager. You validate the response to make sure it is correct. You review the response and approve the execution result." + COMPLETION_PROMPT
    )

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

    groupchat = GroupChat(agents=[admin_user_proxy_agent, data_engineer_agent,
                                  sr_data_analyst_agent, product_manager_agent], messages=[], max_round=10)
    manager = GroupChatManager(
        groupchat=groupchat, llm_config=gpt4_config)
    
    admin_user_proxy_agent.initiate_chat(manager, clear_history=True, message=prompt)


if __name__ == "__main__":
    main()
    db.__exit__(None, None, None)
