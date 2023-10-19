import argparse
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

POSTGRES_TABLE_DEFINITIONS_CAP_REF = "TABLE_DEFINITIONS"
TABLE_RESPONSE_FORMAT_CAP_REF = "TABLE_RESPONSE_FORMAT"

SQL_QUERY_DELIMITER = '-----------'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", help="The prompt for the AI model")
    args = parser.parse_args()

    with PostgresDB() as db:
        db.connect_with_url(DB_URL)
        table_definitions = db.get_table_definitions_for_prompt()

    prompt = args.prompt

    prompt_with_table_definitions = llm.add_cap_ref(
        prompt,
        f"Use these {TABLE_RESPONSE_FORMAT_CAP_REF} to satisfy the database query.",
        POSTGRES_TABLE_DEFINITIONS_CAP_REF,
        table_definitions)

    prompt_with_table_definitions = llm.add_cap_ref(
        prompt_with_table_definitions,
        f"Response in this format {TABLE_RESPONSE_FORMAT_CAP_REF}",
        TABLE_RESPONSE_FORMAT_CAP_REF,
        f"""
            <explanation of the sql query>
            {SQL_QUERY_DELIMITER}
            <sql query exclusively as raw text>
        """
    )

    prompt_response = llm.prompt(prompt_with_table_definitions)

    sql_response = prompt_response.split(SQL_QUERY_DELIMITER)[1]
    print("Prompt Response: ", prompt_response)
    print("Sql Response: ", sql_response)
    db.connect_with_url(DB_URL)
    result = db.run_sql(sql_response)

    print("-------- AGENT RESULT --------")

    print(result)


if __name__ == "__main__":
    main()
