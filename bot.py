import discord
from discord.ext import commands
import json
import os
import re

# -----------------------------
# Set up intents
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True  # required to read message content

bot = commands.Bot(command_prefix="!", intents=intents)

# -----------------------------
# File to store counts
DATA_FILE = "ok_counts.json"

# Load existing counts
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        user_ok_counts = json.load(f)
else:
    user_ok_counts = {}

# Save counts function
def save_counts():
    with open(DATA_FILE, "w") as f:
        json.dump(user_ok_counts, f)

# -----------------------------
# Count function
def count_ok(message_content):
    total = 0
    # Find all standalone ok sequences (\bok(?:ok)*\b)
    matches = re.findall(r'\bok(?:ok)*\b', message_content.lower())
    for match in matches:
        # "ok" counts as 1, "okok" counts as 2, etc.
        total += len(match) // 2
    return total

# -----------------------------
# Bot ready
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

# -----------------------------
# On message event
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return  # ignore self

    ok_count = count_ok(message.content)
    if ok_count > 0:
        user_id = str(message.author.id)
        user_ok_counts[user_id] = user_ok_counts.get(user_id, 0) + ok_count
        save_counts()
        await message.channel.send(f"{message.author.mention} has {user_ok_counts[user_id]} ok's")

    await bot.process_commands(message)  # allow commands to work

# -----------------------------
# Command to check ok count
@bot.command()
async def okcount(ctx, member: discord.Member = None):
    member = member or ctx.author
    user_id = str(member.id)
    count = user_ok_counts.get(user_id, 0)
    await ctx.send(f"{member.mention} has {count} ok's")

# -----------------------------
# Run the bot using environment variable
bot.run(os.environ["DISCORD_TOKEN"])
