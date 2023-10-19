from postgres_da_ai_agent.modules.db import PostgresDB
from postgres_da_ai_agent.modules import llm

import os
import dotenv

dotenv.load_dotenv()

assert os.environ.get(
    "DATABASE_URL"), "POSTGRES_CONNECTION_URL not found in .env file"
assert os.environ.get(
    "OPENAI_API_KEY"), "OPENAI_API_KEY not found in .env file"

DB_URL = os.environ.get("DATABASE_URL")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")


import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("prompt", help="The prompt for the AI model")
    args = parser.parse_args()

    with PostgresDB() as db:
        db.connect_with_url(DB_URL)
        table_definitions = db.get_table_definitions_for_prompt()

    prompt_with_table_definitions = llm.add_cap_ref(args.prompt, "Here are the table definitions:", "TABLE_DEFINITIONS", table_definitions)
    prompt_response = llm.prompt(prompt_with_table_definitions)

    SQL_QUERY_DELIMITER = '-----------'
    sql_response = prompt_response.split(SQL_QUERY_DELIMITER)[1]

    print("SQL Response:", sql_response)


if __name__ == "__main__":
    main()
