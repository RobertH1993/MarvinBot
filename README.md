# MarvinBot
A Matrix chatbot written in python for the hackerspace Hack42.

# configuring
To get the bot up and running a config file should be created, for now a basic config files suffice and an example of such config is given in config.json.example. Most import are the credentials for the Matrix account to be used by the bot.
Please note that the bot itself will update this config file with dynamic parameters, such as the user_id as given by the server on first logon.

# Adding commands
To add a command a handler should be created. This is a class located inside the handlers.py file. Every handler has an reference to the active bot class, the bot class exposes serveral functions for the handlers to use.
When a handler is created it should be registered. For now this is done by calling the register_command_handler function on the bot instance, the best place to do this is inside the main.py

