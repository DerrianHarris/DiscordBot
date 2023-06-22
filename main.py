import os
import logging
import discord
from typing import Optional
from dotenv import load_dotenv
from discord import app_commands
from ApexHostingApi import ApexHostingApi

load_dotenv()

SERVER_ID=os.getenv('SERVER_ID')
CHANNEL_ID=int(os.getenv('CHANNEL_ID'))
DISCORD_TOKEN=os.getenv('DISCORD_TOKEN')
LOG_LEVEL=os.getenv('LOG_LEVEL')
ROLE_NAME=os.getenv('ROLE_NAME')

MY_GUILD = discord.Object(id=SERVER_ID)

class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        # A CommandTree is a special type that holds all the application command
        # state required to make it work. This is a separate class because it
        # allows all the extra state to be opt-in.
        # Whenever you want to work with application commands, your tree is used
        # to store and work with them.
        # Note: When using commands.Bot instead of discord.Client, the bot will
        # maintain its own tree instead.
        self.tree = app_commands.CommandTree(self)

    # In this basic example, we just synchronize the app commands to one guild.
    # Instead of specifying a guild to every command, we copy over our global commands instead.
    # By doing so, we don't have to wait up to an hour until they are shown to the end-user.
    async def setup_hook(self):
        # This copies the global commands over to your guild.
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)

aph=ApexHostingApi(headless=True,min_timeout=10,max_timeout=15)
logging.basicConfig(format='%(asctime)s: [%(levelname)s] %(message)s',level=int(LOG_LEVEL), handlers=[
        logging.FileHandler("discord.log"),
        logging.StreamHandler()
    ])


intents = discord.Intents.default()
client = MyClient(intents=intents)


@client.event
async def on_ready():
    logging.info(f'Logged in as {client.user} (ID: {client.user.id})')
    logging.info('------')


@client.tree.command()
async def get_server_status(interaction: discord.Interaction):
    """Gets Current Server Status"""
    log_requests(interaction, f'get_server_status')
    role = discord.utils.get(interaction.guild.roles, name=ROLE_NAME)
    user = interaction.user
    channel = interaction.channel
    if CHANNEL_ID is not None and channel.id != CHANNEL_ID:
        await interaction.response.send_message(f"This is the wrong channel!")
        return
    if role is not None and role not in interaction.user.roles:
        await interaction.response.send_message(f"{user.name} does not have the correct role! Role: {ROLE_NAME}")
        return
    await interaction.response.defer()
    Status_Message = "Sorry, I could not load the server status. :("
    try:
        aph.login()
        Status_Message = f'```Current server status: {aph.get_server_status()}```'
    except Exception as err:
        logging.error(err)
    await interaction.followup.send(Status_Message)

@client.tree.command()
async def start_server(interaction: discord.Interaction):
    """Starts the server"""
    log_requests(interaction, f'start_server')
    user = interaction.user
    role = discord.utils.get(interaction.guild.roles, name=ROLE_NAME)
    channel = interaction.channel
    if CHANNEL_ID is not None and channel.id != CHANNEL_ID:
        await interaction.response.send_message(f"This is the wrong channel!")
        return
    if role is not None and role not in interaction.user.roles:
        await interaction.response.send_message(f"{user.name} does not have the correct role! Role: {ROLE_NAME}")
        return
    command_msg = "Sorry, I could not start the server. :("
    await interaction.response.defer()
    try:
        aph.login()
        aph.start_server()
        command_msg = f'```Command Sent Successfully!```'
    except Exception as err:
        logging.error(err)
    await interaction.followup.send(command_msg)

@client.tree.command()
async def stop_server(interaction: discord.Interaction):
    """Stops the server"""
    log_requests(interaction, f'stop_server')
    user = interaction.user
    role = discord.utils.get(interaction.guild.roles, name=ROLE_NAME)
    channel = interaction.channel
    if CHANNEL_ID is not None and channel.id != CHANNEL_ID:
        await interaction.response.send_message(f"This is the wrong channel!")
        return
    if role is not None and role not in interaction.user.roles:
        await interaction.response.send_message(f"{user.name} does not have the correct role! Role: {ROLE_NAME}")
        return
    await interaction.response.defer()
    command_msg = "Sorry, I could not stop the server. :("
    try:
        aph.login()
        aph.stop_server()
        command_msg = f'```Command Sent Successfully!```'
    except Exception as err:
        logging.error(err)
    await interaction.followup.send(command_msg)

@client.tree.command()
async def restart_server(interaction: discord.Interaction):
    """Restarts the server"""
    log_requests(interaction, f'restart_server')
    role = discord.utils.get(interaction.guild.roles, name=ROLE_NAME)
    user = interaction.user
    channel = interaction.channel
    if CHANNEL_ID is not None and channel.id != CHANNEL_ID:
        await interaction.response.send_message(f"This is the wrong channel!")
        return
    if role is not None and role not in interaction.user.roles:
        await interaction.response.send_message(f"{user.name} does not have the correct role! Role: {ROLE_NAME}")
        return

    await interaction.response.defer()
    command_msg = "Sorry, I could not restart the server. :("
    try:
        aph.login()
        aph.restart_server()
        command_msg = f'```Command Sent Successfully!```'
    except Exception as err:
        logging.error(err)
    await interaction.followup.send(command_msg)

@client.tree.command()
async def force_stop_server(interaction: discord.Interaction):
    """Force stops the server"""
    log_requests(interaction, f'force_stop_server')
    role = discord.utils.get(interaction.guild.roles, name=ROLE_NAME)
    user = interaction.user
    channel = interaction.channel
    if CHANNEL_ID is not None and channel.id != CHANNEL_ID:
        await interaction.response.send_message(f"This is the wrong channel!")
        return
    if role is not None and role not in interaction.user.roles:
        await interaction.response.send_message(f"{user.name} does not have the correct role! Role: {ROLE_NAME}")
        return

    await interaction.response.defer()
    command_msg = "Sorry, I could not force stop the server. :("
    try:
        aph.login()
        aph.force_stop_server()
        command_msg = f'```Command Sent Successfully!```'
    except Exception as err:
        logging.error(err)
    await interaction.followup.send(command_msg)

@client.tree.command()
@app_commands.describe(
    command='Command you want to run on the console',
)
async def run_console_command(interaction: discord.Interaction, command: str):
    """Run a command using the server console log"""
    log_requests(interaction, f'run_console_command [command={command}]')
    role = discord.utils.get(interaction.guild.roles, name=ROLE_NAME)
    user = interaction.user
    channel = interaction.channel

    if CHANNEL_ID is not None and channel.id != CHANNEL_ID:
        await interaction.response.send_message(f"This is the wrong channel!")
        return
    if role is not None and role not in interaction.user.roles:
        await interaction.response.send_message(f"{user.name} does not have the correct role! Role: {ROLE_NAME}")
        return

    await interaction.response.defer()
    command_msg = "Sorry, I could not send the command. :("
    try:
        aph.login()
        aph.run_console_command(command)
        command_msg = f'```Command Sent Successfully!```'
    except Exception as err:
        logging.error(err)
    await interaction.followup.send(command_msg)

# To make an argument optional, you can either give it a supported default argument
# or you can mark it as Optional from the typing standard library. This example does both.
@client.tree.command()
@app_commands.describe(lines='The number of lines you want from the logs. Min: 1 Max: 20 Default: 10')
async def get_console_log(interaction: discord.Interaction, lines: Optional[app_commands.Range[int, 1, 20]] = 10):
    """Returns last messages from console logs. Defaults to 10"""
    log_requests(interaction,f'get_console_log [lines={lines}]')
    role = discord.utils.get(interaction.guild.roles, name=ROLE_NAME)
    user = interaction.user
    channel = interaction.channel

    if CHANNEL_ID is not None and channel.id != CHANNEL_ID:
        await interaction.response.send_message(f"This is the wrong channel!")
        return
    if role is not None and role not in interaction.user.roles:
        await interaction.response.send_message(f"{user.name} does not have the correct role! Role: {ROLE_NAME}")
        return
    await interaction.response.defer()
    Log_Message = "Sorry, I could not load the console log. :("
    try:
        aph.login()
        console_log = aph.get_console_log(lines)
        console_log = '\n'.join(console_log)
        Log_Message = f'## Console Log\nLast {lines} lines```{console_log}```'
    except Exception as err:
        logging.error(err)
    await interaction.followup.send(Log_Message)

def log_requests(interaction: discord.Interaction,command: str):
    user = interaction.user
    channel = interaction.channel
    logging.info(f'Username: {user.name} | Channel: {channel} | Roles: {user.roles} | Request: {interaction.command.name}')

client.run(DISCORD_TOKEN)