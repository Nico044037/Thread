import discord
from discord.ext import commands
from discord.ui import View, Button
import os

TOKEN = os.getenv("TOKEN")

FORUM_CHANNEL_ID = 1484245651284951091
MOD_CHANNEL_ID = 1487886918556455013


intents = discord.Intents.default()
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)


class ApprovalView(View):
    def __init__(self, thread: discord.Thread):
        super().__init__(timeout=None)
        self.thread = thread

    @discord.ui.button(label="✅ Accept", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button: Button):
        if not interaction.user.guild_permissions.manage_threads:
            await interaction.response.send_message("No permission.", ephemeral=True)
            return

        try:
            await self.thread.send("@everyone ✅ Post approved!")
            await interaction.response.send_message("✅ Approved.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Error: {e}", ephemeral=True)

    @discord.ui.button(label="❌ Reject", style=discord.ButtonStyle.red)
    async def reject(self, interaction: discord.Interaction, button: Button):
        if not interaction.user.guild_permissions.manage_threads:
            await interaction.response.send_message("No permission.", ephemeral=True)
            return

        try:
            await self.thread.delete()
            await interaction.response.send_message("❌ Deleted thread.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Error: {e}", ephemeral=True)


@bot.event
async def on_thread_create(thread: discord.Thread):
    # Only trigger for your forum channel
    if thread.parent_id != FORUM_CHANNEL_ID:
        return

    mod_channel = bot.get_channel(MOD_CHANNEL_ID)
    if not mod_channel:
        return

    view = ApprovalView(thread)

    await mod_channel.send(
        f"🆕 New forum post: **{thread.name}**\n"
        f"🔗 Jump to post: {thread.jump_url}\n\n"
        f"Approve or reject:",
        view=view
    )


@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")


bot.run(TOKEN)
