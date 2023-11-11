from autogen import config_list_from_models

base_config = {
    "use_cache": False,
    "temperature": 0,
    "config_list": config_list_from_models(["gpt-4"]),
    "request_timeout": 120,
}

gpt4_config = {
    **base_config,
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

# write file configuration

write_file_config = {
    **base_config,
    "functions": [
        {
            "name": "write_file",
            "description": "Write text to a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_name": {
                        "type": "string",
                        "description": "File name to write to",
                    },
                    "content": {
                        "type": "string",
                        "description": "Text to write to the file",
                    },
                },
                "required": ["file_name", "content"],
            }
        }
    ]
}