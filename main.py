import asyncio
import os
import logging
import time
import pytz
from datetime import datetime, timezone
from datetime import timedelta

import discord
from typing import Optional
from dotenv import load_dotenv
from discord import app_commands
from ApexHostingApi import ApexHostingApi

load_dotenv()

SERVER_ID = os.getenv('SERVER_ID')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
MAX_RETRIES = int(os.getenv('MAX_RETRIES'))
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
LOG_LEVEL = os.getenv('LOG_LEVEL')
ROLE_NAME = os.getenv('ROLE_NAME')

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


aph = ApexHostingApi(headless=True, min_timeout=10, max_timeout=15)
logging.basicConfig(format='%(asctime)s: [%(levelname)s] %(message)s', level=int(LOG_LEVEL), handlers=[
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
    await check_request(interaction)
    await interaction.response.defer()
    command_msg = await run_server_command(aph.get_server_status)
    command_msg = f"```Current server status: {command_msg}```"
    await interaction.followup.send(command_msg)


@client.tree.command()
async def start_server(interaction: discord.Interaction):
    """Starts the server"""
    log_requests(interaction, f'start_server')
    await check_request(interaction)
    await interaction.response.defer()
    command_msg = await run_server_command(aph.start_server)
    command_msg = f'```{command_msg}```'
    await interaction.followup.send(command_msg)

@client.tree.command()
async def stop_server(interaction: discord.Interaction):
    """Stops the server"""
    log_requests(interaction, f'stop_server')
    await check_request(interaction)
    await interaction.response.defer()
    command_msg = await run_server_command(aph.stop_server)
    command_msg = f'```{command_msg}```'
    await interaction.followup.send(command_msg)


@client.tree.command()
@app_commands.describe(minutes='The minutes to wait before stopping the server. Min: 1 Max: 30 Default: 15')
async def safe_stop_server(interaction: discord.Interaction, minutes: Optional[app_commands.Range[int, 1, 30]] = 15):
    """Stops the server after the duration given by the requester"""
    log_requests(interaction, f'safe_stop_server')
    await check_request(interaction)
    await interaction.response.defer()
    command_msg = await run_server_command(aph.stop_server,interaction=interaction,minutes=minutes)
    command_msg = f'```{command_msg}```'
    await interaction.followup.send(command_msg)


@client.tree.command()
async def restart_server(interaction: discord.Interaction):
    """Restarts the server"""
    log_requests(interaction, f'restart_server')
    await check_request(interaction)
    await interaction.response.defer()
    command_msg = await run_server_command(aph.restart_server)
    command_msg = f'```{command_msg}```'
    await interaction.followup.send(command_msg)


@client.tree.command()
async def force_stop_server(interaction: discord.Interaction):
    """Force stops the server"""
    log_requests(interaction, f'force_stop_server')
    await check_request(interaction)
    await interaction.response.defer()
    command_msg = await run_server_command(aph.force_stop_server)
    command_msg = f'```{command_msg}```'
    await interaction.followup.send(command_msg)


@client.tree.command()
@app_commands.describe(
    command='Command you want to run on the console',
)
async def run_console_command(interaction: discord.Interaction, command: str):
    """Run a command using the server console log"""
    log_requests(interaction, f'run_console_command [command={command}]')
    await check_request(interaction)
    await interaction.response.defer()
    command_msg = await run_server_command(aph.run_console_command,param=command)
    command_msg = f'```{command_msg}```'
    await interaction.followup.send(command_msg)


# To make an argument optional, you can either give it a supported default argument
# or you can mark it as Optional from the typing standard library. This example does both.
@client.tree.command()
@app_commands.describe(lines='The number of lines you want from the logs. Min: 1 Max: 20 Default: 10')
async def get_console_log(interaction: discord.Interaction, lines: Optional[app_commands.Range[int, 1, 20]] = 10):
    """Returns last messages from console logs. Defaults to 10"""
    log_requests(interaction, f'get_console_log [lines={lines}]')
    await check_request(interaction)
    await interaction.response.defer()
    command_msg = await run_server_command(aph.run_console_command,param=lines)
    command_msg = f"## Console Log\nLast {lines} lines\n```{command_msg}```"
    await interaction.followup.send(command_msg)


def log_requests(interaction: discord.Interaction, command: str):
    user = interaction.user
    channel = interaction.channel
    logging.info(f'Username: {user.name} | Channel: {channel} | Roles: {user.roles} | Request: {command}')

async def run_server_command(func,interaction: discord.Interaction=None,minutes=0,param=None):
    command_msg = f'```Sorry I could not process the request! :(```'
    try:
        if minutes >= 0 and interaction is not None:
            stop_time = datetime.now(pytz.timezone('US/Central')) + timedelta(minutes=minutes)
            stop_time_str = stop_time.strftime("%I:%M %p")
            logging.info(f'Starting sleep for {minutes} min! Stop time: {stop_time_str}')
            await interaction.channel.send(f'```Stopping sever at: {stop_time_str}```')
            await asyncio.sleep(60 * minutes)
        await retry_async(aph.login, max_tries=MAX_RETRIES)
        result = None
        if param is not None:
            result = await retry_async(func, max_tries=MAX_RETRIES)
        else:
            result = await retry_async(func,param=param, max_tries=MAX_RETRIES)

        if result is not None:
            command_msg = f'{result}'
        else:
            command_msg = f'Command Sent Successfully!'
    except Exception as err:
        logging.error(err)
    logging.info(f"Command result message: {command_msg}")
    return command_msg

async def check_request(interaction: discord.Interaction):
    role = discord.utils.get(interaction.guild.roles, name=ROLE_NAME)
    user = interaction.user
    channel = interaction.channel

    if CHANNEL_ID is not None and channel.id != CHANNEL_ID:
        await interaction.response.send_message(f"This is the wrong channel!")
        return
    if role is not None and role not in interaction.user.roles:
        await interaction.response.send_message(f"{user.name} does not have the correct role! Role: {ROLE_NAME}")
        return


def retry(func, param=None, max_tries=2):
    count = 0
    result = ''
    while count < max_tries:
        try:
            if param is not None:
                result = func(param)
            else:
                result = func()
        except Exception:
            count += 1
            if (count >= max_tries):
                logging.info(f'Max retries reached: {func}')
                raise
            time.sleep(2)
            logging.info(f'Retrying Last Function call: {func}')
            continue
        return result


async def retry_async(func, param=None, max_tries=2):
    count = 0
    result = ''
    while count < max_tries:
        try:
            if param is not None:
                result = await func(param)
            else:
                result = await func()
        except Exception:
            count += 1
            if (count >= max_tries):
                logging.info(f'Max retries reached: {func}')
                raise
            time.sleep(2)
            logging.info(f'Retrying Last Function call: {func}')
            continue
        return result


client.run(DISCORD_TOKEN)
