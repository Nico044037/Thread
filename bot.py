import discord
from discord.ext import commands
from discord.ui import View, Button
import os

TOKEN = os.getenv("TOKEN")

FORUM_CHANNEL_ID = 1484245651284951091
MOD_CHANNEL_ID = 1487886918556455013


intents = discord.Intents.default()
intents.guilds = True
intents.members = True  # needed to fetch users

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
            # 👇 Get thread creator
            owner = self.thread.owner

            # 👇 Try DM
            if owner:
                try:
                    await owner.send(
                        f"❌ Your post **'{self.thread.name}'** was rejected by moderators."
                    )
                except:
                    pass  # user might have DMs closed

            await self.thread.delete()

            await interaction.response.send_message(
                "❌ Thread deleted and user notified.", ephemeral=True
            )

        except Exception as e:
            await interaction.response.send_message(f"Error: {e}", ephemeral=True)


@bot.event
async def on_thread_create(thread: discord.Thread):
    if thread.parent_id != FORUM_CHANNEL_ID:
        return

    mod_channel = bot.get_channel(MOD_CHANNEL_ID)
    if not mod_channel:
        return

    view = ApprovalView(thread)

    await mod_channel.send(
        f"🆕 New forum post: **{thread.name}**\n"
        f"👤 Author: {thread.owner.mention if thread.owner else 'Unknown'}\n"
        f"🔗 {thread.jump_url}",
        view=view
    )


@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")


bot.run(TOKEN)
