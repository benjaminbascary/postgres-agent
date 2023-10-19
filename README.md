## POSTGRES AGENT ##

Requirements:

* poetry installed locally

Poetry docs: https://python-poetry.org/docs/ (package manager)

* python 3.11 or higher installed

Steps

```
cp .env.example .env
```
Fill .env file with your OpenAI api-key and a postgress connection string

Example: postgresql://user:password@127.0.0.1:5432/databasename

```
poetry install
```

Try for yourself:

```
poetry run start --prompt="Your prompt"
```

Example: "Get me the locations with the name Bariloche"

Or: "Get me the users created after September 23"

You will get something like this:

```
Sure, Here is your response:

We want to find locations that match the name 'barrancas'. The table in the database that stores location information is named 'location'. Therefore, we need to look into this table.
-----------
SELECT * FROM location WHERE name = 'barrancas'
-------- AGENT RESULT --------
[('d81093b8-36a8-4724-9782-8982d04148e9', 'barrancas', 10.95667, -72.788872, None)]
```


### NOTE:

Use the agent over a trash database or a cloned one. Using an agente can lead to deletions or unexpected behavior XD

## You might get wrong answers, so feel free to debug, improve the prompt, make suggestions or even contribute!

### Example video

https://www.youtube.com/watch?v=v2JdFJbVyik&ab_channel=BenjaminBascary
