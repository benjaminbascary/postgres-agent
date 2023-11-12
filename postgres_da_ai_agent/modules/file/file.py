def write_file(file_name, content):
    with open(f"report/{file_name}", "w") as file:
        file.write(content)
