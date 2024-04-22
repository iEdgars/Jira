import json
import os

def migrateCreds():
    try:
        # Load credentials
        with open('jiraCreds.json') as jiraCredsFile:
            jiraCreds = json.load(jiraCredsFile)

        email = jiraCreds['email']
        apiToken = jiraCreds['apiToken']

        # Check if .env file exists, if not create one
        if not os.path.exists('.env'):
            with open('.env', 'w') as env_file:
                env_file.write(f'email="{email}"\n')
                env_file.write(f'apiToken={apiToken}\n')

            os.remove('jiraCreds.json')
    except FileNotFoundError:
        # Check if .env file exists, if not create one
        if not os.path.exists('.env'):
            with open('.env', 'w') as env_file:
                env_file.write(f'email=""\n')
                env_file.write(f'apiToken=\n')