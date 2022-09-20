import discord
from discord.ext import commands


class MiscCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    # https://stackoverflow.com/a/73504139/19106293
    @commands.slash_command(name="help", description="Stop it. Get some help.")
    async def help(self, ctx: discord.ApplicationContext,
                   command: discord.Option(discord.SlashCommandOptionType.string, "command", required=False, default=None)):

        all_commands = [command.name for command in self.client.all_commands.values()]

        help_embed = discord.Embed(title="DaddyBot Help")
        command_names_list = [x for x in all_commands]

        if not command:
            help_embed.add_field(
                name="List of supported commands:",
                value="\n".join([str(i + 1) + ". " + x for i, x in enumerate(all_commands)]),
                inline=False
            )
            help_embed.add_field(
                name="Details",
                value="Type `/help <command name>` for more details about each command.",
                inline=False
            )

        elif command in command_names_list:
            if not hasattr(self.client.get_command(command), "description"):
                help_embed.add_field(
                    name=command,
                    value="No description found."
                )
            else:
                help_embed.add_field(
                    name=command,
                    value=self.client.get_command(command).description
                )

        else:
            help_embed.add_field(
                name="Uh oh.",
                value="That command wasn't found. Ooops"
            )

        await ctx.send(embed=help_embed)

    @commands.slash_command(name="ping", description="Get the bot's latency")
    async def ping(self, ctx):
        await ctx.send(f"Pong! Latency: {round(self.client.latency, 2)}ms")
