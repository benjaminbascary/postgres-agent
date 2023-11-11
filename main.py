import os
import dotenv
import argparse
from postgres_da_ai_agent.modules.orchestrator.orchestrator import Orchestrator
from postgres_da_ai_agent.modules.db.db import PostgresDB
from postgres_da_ai_agent.modules.prompts.prompts import (
    get_first_instruction_pompt,
)
from postgres_da_ai_agent.modules.agents.agents import (
    admin_user_proxy_agent,
    data_engineer_agent,
    sr_data_analyst_agent,
    product_manager_agent,
    text_report_agent,
)

dotenv.load_dotenv()

assert os.environ.get(
    "DATABASE_URL"), "POSTGRES_CONNECTION_URL not found in .env file"
assert os.environ.get(
    "OPENAI_API_KEY"), "OPENAI_API_KEY not found in .env file"

DB_URL = os.environ.get("DATABASE_URL")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

AGENT_TEAM_NAME = "::: 🤖 Postgres Data Analytics Multi-Agent Team 🤖 :::"
VIZ_AGENT_TEAM_NAME = "::: 🤖 Postgres Data Analytics Viz Team 🤖 :::"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", help="The prompt for the AI model")
    args = parser.parse_args()

    db = PostgresDB()
    db.connect_with_url(DB_URL)
    table_definitions = db.get_table_definitions_for_prompt()

    prompt = args.prompt

    prompt = get_first_instruction_pompt(prompt, table_definitions)

    """
        Sequential agents
    """

    data_engineering_agents = [
        admin_user_proxy_agent,
        data_engineer_agent,
        sr_data_analyst_agent,
        product_manager_agent,
    ]

    data_engineer_agent_orchestrator = Orchestrator(
        name=AGENT_TEAM_NAME,
        agents=data_engineering_agents,
    )

    success, data_engineer_messages = data_engineer_agent_orchestrator.sequential_conversation(
        prompt)

    # Here we grab the last message not being APPROVED
    data_analyst_result = data_engineer_messages[-6]

    # Broadcasting agents

    data_viz_agents = [
        admin_user_proxy_agent,
        text_report_agent,
    ]

    data_viz_orchestrator = Orchestrator(
        name=VIZ_AGENT_TEAM_NAME,
        agents=data_viz_agents,
    )

    data_viz_prompt = f"Here is the data to report: {data_analyst_result}"

    data_viz_orchestrator.broadcast_conversation(data_viz_prompt)


if __name__ == "__main__":
    main()
