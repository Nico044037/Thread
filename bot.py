import discord
from discord.ext import commands
from discord.ui import View, Button
import os

TOKEN = os.getenv("TOKEN")

TARGET_CHANNEL_ID = 1484245651284951091  # channel where threads are created


intents = discord.Intents.default()
intents.guilds = True
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents)


class ApprovalView(View):
    def __init__(self, thread: discord.Thread):
        super().__init__(timeout=None)
        self.thread = thread

    @discord.ui.button(label="✅ Accept", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button: Button):
        # OPTIONAL: restrict to admins
        if not interaction.user.guild_permissions.manage_threads:
            await interaction.response.send_message("No permission.", ephemeral=True)
            return

        try:
            await self.thread.send("@everyone ✅ Thread approved!")
            await interaction.response.send_message("Thread accepted.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Error: {e}", ephemeral=True)

    @discord.ui.button(label="❌ Reject", style=discord.ButtonStyle.red)
    async def reject(self, interaction: discord.Interaction, button: Button):
        if not interaction.user.guild_permissions.manage_threads:
            await interaction.response.send_message("No permission.", ephemeral=True)
            return

        try:
            await self.thread.delete()
            await interaction.response.send_message("Thread deleted.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Error: {e}", ephemeral=True)


@bot.event
async def on_thread_create(thread: discord.Thread):
    if thread.parent_id != TARGET_CHANNEL_ID:
        return

    channel = bot.get_channel(TARGET_CHANNEL_ID)

    if not channel:
        return

    view = ApprovalView(thread)

    await channel.send(
        f"🆕 New thread: **{thread.name}**\nApprove or reject:",
        view=view
    )


@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")


bot.run(TOKEN)
