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

# from ApexHostingApi import ApexHostingApi
from NitradoApi import NitradoApi

load_dotenv()

SERVER_ID = os.getenv("SERVER_ID")
CHANNEL_NAME = os.getenv("CHANNEL_NAME")
MAX_RETRIES = int(os.getenv("MAX_RETRIES"))
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
LOG_LEVEL = os.getenv("LOG_LEVEL")
ROLE_NAME = os.getenv("ROLE_NAME")
ERROR_MESSAGE = "Sorry, I could not process this request! :("
FIRST_RESPONSE_MESSAGE = "Request received! :)"


aph = None  # ApexHostingApi(headless=True, min_timeout=10, max_timeout=15)
napi = NitradoApi()
logging.basicConfig(
    format="%(asctime)s: [%(levelname)s] %(message)s",
    level=int(LOG_LEVEL),
    handlers=[logging.FileHandler("discord.log"), logging.StreamHandler()],
)

USE_NITRADO = True

intents = discord.Intents.default()
intents.members = True

bot = discord.Bot(intents=intents)
bot.auto_sync_commands = True


@bot.event
async def on_ready():
    logging.info(f"Logged in as {bot.user} (ID: {bot.user.id})")
    logging.info("------")


@bot.command()
async def get_server_status(interaction: discord.Interaction):
    """Gets Current Server Status"""
    log_requests(interaction, f"get_server_status")
    await check_request(interaction)
    await interaction.response.send_message(
        f"```{FIRST_RESPONSE_MESSAGE}```", ephemeral=True
    )
    if USE_NITRADO:
        command_msg = await run_server_command(napi.get_server_status)
    else:
        command_msg = await run_server_command(aph.get_server_status)
    if command_msg is not None:
        command_msg = f"```Current server status: {command_msg}```"
    else:
        command_msg = f"```{ERROR_MESSAGE}```"
    await interaction.channel.send(command_msg)


@bot.command()
async def start_server(interaction: discord.Interaction):
    """Starts the server"""
    log_requests(interaction, f"start_server")
    await check_request(interaction)
    await interaction.response.send_message(
        f"```{FIRST_RESPONSE_MESSAGE}```", ephemeral=True
    )
    if USE_NITRADO:
        command_msg = await run_server_command(napi.start_server)
    else:
        command_msg = await run_server_command(aph.start_server)
    if command_msg is not None:
        command_msg = f"```{command_msg}```"
    else:
        command_msg = f"```{ERROR_MESSAGE}```"
    await interaction.channel.send(command_msg)


@bot.command()
async def stop_server(interaction: discord.Interaction):
    """Stops the server"""
    log_requests(interaction, f"stop_server")
    await check_request(interaction)
    await interaction.response.send_message(
        f"```{FIRST_RESPONSE_MESSAGE}```", ephemeral=True
    )
    if USE_NITRADO:
        command_msg = await run_server_command(napi.stop_server)
    else:
        command_msg = await run_server_command(aph.stop_server)
    if command_msg is not None:
        command_msg = f"```{command_msg}```"
    else:
        command_msg = f"```{ERROR_MESSAGE}```"
    await interaction.channel.send(command_msg)


@bot.command()
async def safe_stop_server(
    ctx,
    minutes: discord.Option(
        int,
        "The minutes to wait before stopping the server. Min: 1 Max: 30 Default: 15",
        min_value=1,
        max_value=30,
        default=15,
    ),
):
    """Stops the server after the duration given by the requester"""
    log_requests(ctx, f"safe_stop_server")
    await check_request(ctx)
    await ctx.response.send_message(f"```{FIRST_RESPONSE_MESSAGE}```", ephemeral=True)
    if USE_NITRADO:
        command_msg = await run_server_command(
            napi.stop_server, interaction=ctx, minutes=minutes
        )
    else:
        command_msg = await run_server_command(
            aph.stop_server, interaction=ctx, minutes=minutes
        )
    if command_msg is not None:
        command_msg = f"```{command_msg}```"
    else:
        command_msg = f"```{ERROR_MESSAGE}```"
    await ctx.channel.send(command_msg)


@bot.command()
async def restart_server(interaction: discord.Interaction):
    """Restarts the server"""
    log_requests(interaction, f"restart_server")
    await check_request(interaction)
    await interaction.response.send_message(
        f"```{FIRST_RESPONSE_MESSAGE}```", ephemeral=True
    )
    if USE_NITRADO:
        command_msg = await run_server_command(napi.restart_server)
    else:
        command_msg = await run_server_command(aph.restart_server)
    if command_msg is not None:
        command_msg = f"```{command_msg}```"
    else:
        command_msg = f"```{ERROR_MESSAGE}```"
    await interaction.channel.send(command_msg)


@bot.command()
async def force_stop_server(interaction: discord.Interaction):
    """Force stops the server"""
    log_requests(interaction, f"force_stop_server")
    await check_request(interaction)
    await interaction.response.send_message(
        f"```{FIRST_RESPONSE_MESSAGE}```", ephemeral=True
    )
    if USE_NITRADO:
        command_msg = "Command not yet supported for this server"
    else:
        command_msg = await run_server_command(aph.restart_server)
    if command_msg is not None:
        command_msg = f"```{command_msg}```"
    else:
        command_msg = f"```{ERROR_MESSAGE}```"
    await interaction.channel.send(command_msg)


@bot.command()
async def run_console_command(
    interaction: discord.Interaction,
    command: discord.Option(str, "Command you want to run on the console"),
):
    """Run a command using the server console log"""
    log_requests(interaction, f"run_console_command [command={command}]")
    await check_request(interaction)
    await interaction.response.send_message(
        f"```{FIRST_RESPONSE_MESSAGE}```", ephemeral=True
    )
    if USE_NITRADO:
        command_msg = await run_server_command(napi.run_console_command, param=command)
    else:
        command_msg = await run_server_command(aph.run_console_command, param=command)
    if command_msg is not None:
        command_msg = f"```{command_msg}```"
    else:
        command_msg = f"```{ERROR_MESSAGE}```"
    await interaction.channel.send(command_msg)


# To make an argument optional, you can either give it a supported default argument
# or you can mark it as Optional from the typing standard library. This example does both.
@bot.command()
async def get_console_log(
    interaction: discord.Interaction,
    lines: discord.Option(
        int,
        "The number of lines you want from the logs. Min: 1 Max: 20 Default: 10",
        min_value=1,
        max_value=20,
        default=10,
    ),
):
    """Returns last messages from console logs. Defaults to 10"""
    log_requests(interaction, f"get_console_log [lines={lines}]")
    await check_request(interaction)
    await interaction.response.send_message(
        f"```{FIRST_RESPONSE_MESSAGE}```", ephemeral=True
    )
    if USE_NITRADO:
        command_msg = "Command not yet supported for this server"
    else:
        command_msg = await run_server_command(aph.run_console_command, param=lines)
    if command_msg is not None:
        command_msg = f"## Console Log\nLast {lines} lines\n```{command_msg}```"
    else:
        command_msg = f"```{ERROR_MESSAGE}```"
    await interaction.channel.send(command_msg)


def log_requests(interaction: discord.Interaction, command: str):
    user = interaction.user
    channel = interaction.channel
    logging.info(
        f"Username: {user.name} | Channel: {channel} | Roles: {user.roles} | Request: {command}"
    )


async def run_server_command(
    func, interaction: discord.Interaction = None, minutes=0, param=None
):
    command_msg = None
    try:
        if minutes >= 0 and interaction is not None:
            stop_time = datetime.now(pytz.timezone("US/Central")) + timedelta(
                minutes=minutes
            )
            stop_time_str = stop_time.strftime("%I:%M %p")
            logging.info(
                f"Starting sleep for {minutes} min! Stop time: {stop_time_str}"
            )
            await interaction.channel.send(f"```Stopping sever at: {stop_time_str}```")
            await asyncio.sleep(60 * minutes)
        if not USE_NITRADO:
            await retry_async(aph.login, max_tries=MAX_RETRIES)
        result = await retry_async(func, param=param, max_tries=MAX_RETRIES)
        if result is not None:
            command_msg = f"{result}"
        else:
            command_msg = f"Command Sent Successfully!"
    except Exception as err:
        logging.error(err)
    logging.info(f"Command result message: {command_msg}")
    return command_msg


async def check_request(interaction: discord.Interaction):
    channel = interaction.channel
    if CHANNEL_NAME is not None and channel.name != CHANNEL_NAME:
        await interaction.response.send_message(
            f"This is the wrong channel!", ephemeral=True
        )
        return
def retry(func, param=None, max_tries=2):
    count = 0
    result = ""
    while count < max_tries:
        try:
            if param is not None:
                result = func(param)
            else:
                result = func()
        except Exception as e:
            count += 1
            if count >= max_tries:
                logging.info(f"Max retries reached: {func}")
                raise
            time.sleep(2)
            logging.error("Exception occurred: %s", e)
            logging.info(f"Retrying Last Function call: {func}")
            continue
        return result


async def retry_async(func, param=None, max_tries=2):
    count = 0
    result = ""
    while count < max_tries:
        try:
            if param is not None:
                result = await func(param)
            else:
                result = await func()
        except Exception as e:
            count += 1
            if count >= max_tries:
                logging.info(f"Max retries reached: {func}")
                raise
            time.sleep(2)
            logging.exception("Exception occurred: %s", e)
            logging.info(f"Retrying Last Function call: {func}")
            continue
        return result


bot.run(DISCORD_TOKEN)
