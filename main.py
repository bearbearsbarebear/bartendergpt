import discord
import openai
import asyncio
from discord import app_commands
from openai.error import APIError, ServiceUnavailableError, RateLimitError

# This code just follows the basic documentation of OpenAi to implement the API
# It's a simple discord bot with two slash commands, 'sync', in case commands aren't properly synched
# and 'ask', to send the question to the API

# I don't use 'interaction.response.send_message' because it sometimes fails.
# while I found that defering the message and sending a followup works better

# The reason to not use 'self.tree.copy_global_to' is that it's known to duplicate global
# with local guild commands. So instead we just use global ones

# Change tokens
BOT_TOKEN = ""
openai.api_key = ""
MY_GUILD = discord.Object(id=)

class Bartender(discord.Client):
	def __init__(self):
		super().__init__(intents=discord.Intents.default())

		# Bot slash commands
		self.tree = app_commands.CommandTree(self)

	async def setup_hook(self):
		#self.tree.copy_global_to(guild=MY_GUILD)
		await self.tree.sync(guild=MY_GUILD)

client = Bartender()

@client.event
async def on_ready():
	print(f'Logged in as {client.user}:{client.user.id}')

# Sync commands from the tree
@client.tree.command()
async def sync(interaction: discord.Interaction):
	synced = await client.tree.sync()

	await interaction.response.defer(ephemeral=True, thinking=True)
	await interaction.followup.send(f"Synced {len(synced)} command{'s' if len(synced) > 1 else ''} globally")
	#await interaction.response.send_message(f"Synced {len(synced)} command{'s' if len(synced) > 1 else ''} globally")

# Command "ask" for questions to OpenAi
@client.tree.command()
@app_commands.describe(question = "Prompt to the OpenAi")
async def ask(interaction: discord.Interaction, question: str):
	res = ""

	try:
		completions = openai.Completion.create(
			engine = "text-davinci-003",
			prompt = question,
			max_tokens = 2048,
			echo = True,
			n = 1,
			stop = None,
			temperature = 0.56,
		)
	except ServiceUnavailableError:
		res += f"OpenAI is not available right now."
	except RateLimitError as e:
		res += f"We are rate limited right now. {e}"
	except APIError:
		res += f"Something is wrong with the API."

	if completions.choices:
		res += f"Response:\n```{completions.choices[0].text}```"

	await interaction.response.defer(ephemeral=True, thinking=True)
	await interaction.followup.send(res)
	#await interaction.channel.send(res)

if __name__ == "__main__":
	client.run(BOT_TOKEN)