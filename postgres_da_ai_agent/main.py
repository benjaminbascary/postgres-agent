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


def main():

    # parse prompt param using arg parse
    with PostgresDB() as db:
        db.connect_with_url(DB_URL)
        locations_table = db.get_all("location")

        print("locations", locations_table)

    # connect to postgres db with statement and create a db_manager class

    # call db_manager.get_table_definition_for_prompt() to get tables in promt ready form

    # create two blank calls to llm.add_cap_ref() that update our current prompt passed in from cli

    # call llm.prompt to get a prompt_response variable

    # parse sql response from prompt_response using SQL_QUERY_DELIMITER '-----------'


if __name__ == "__main__":
    main()
