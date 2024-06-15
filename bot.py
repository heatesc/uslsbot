import os
import discord
from discord.ext import commands
from discord import app_commands
from Projects_Info import Projects_Info
import bot_commands

# Load the bot token from the environment variable
def load_token() -> str:
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
    if DISCORD_TOKEN is None:
        raise ValueError("Error: DISCORD_TOKEN environment variable not set.")
    return DISCORD_TOKEN

async def create_projects_info_message(client, channel_id):
    channel = client.get_channel(int(channel_id))
    if channel is None:
        raise ValueError(f"Channel with ID {channel_id} not found")

    initial_message_content = """
# **Projects Info**
"""

    message = await channel.send(initial_message_content)
    return message.id

def init_bot() -> [discord.Client, app_commands.CommandTree]:
    intents = discord.Intents.default()
    client = discord.Client(intents=intents)
    command_tree = app_commands.CommandTree(client)
    return client, command_tree

async def setup_projects_info(client):
    
    try:
        channel_id = int(os.getenv("PROJECTS_INFO_CHANNEL_ID"))
    except ValueError:
        raise ValueError("Error: PROJECTS_INFO_CHANNEL_ID environment variable not set or invalid")
        return None
    
    try:
        message_id = int(os.getenv("PROJECTS_INFO_MESSAGE_ID"))
    except ValueError:
        raise ValueError("Error: PROJECTS_INFO_MESSAGE_ID environment variable not set or invalid")

    if message_id:
        proj_info = Projects_Info(client, channel_id, message_id)
        if not await proj_info.verify_message_editable():
            print("Specified message is not editable. Creating a new projects info message.")
            message_id = await create_projects_info_message(client, channel_id)
            os.environ["PROJECTS_INFO_MESSAGE_ID"] = str(message_id)
    else:
        print("No message ID specified. Creating a new projects info message.")
        message_id = await create_projects_info_message(client, channel_id)
        os.environ["PROJECTS_INFO_MESSAGE_ID"] = str(message_id)
        print(f"Projects info message created with ID {message_id}")

    return Projects_Info(client, channel_id, message_id)

def main() -> None:
    client, command_tree = init_bot()

    DISCORD_TOKEN = load_token()
    if DISCORD_TOKEN is None:
        return

    @client.event
    async def on_ready():
        try:
            proj_info = await setup_projects_info(client)
            if proj_info is None:
                await client.close()
                return
        except ValueError as e:
            print(e)
            await client.close()
            return

        bot_commands.add_commands(command_tree, proj_info)
        await command_tree.sync()
        print(f'Bot connected as {client.user}')

    client.run(DISCORD_TOKEN)

if __name__ == "__main__":
    main()
