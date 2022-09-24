import discord
from discord.ext import commands


class EventCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Client logged in as {self.client.user.name}.")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        em = discord.Embed(title="Hello Newbie!", description="Welcome to the Daddy Server!")
        em.add_field(name="About Me", value="I am the main bot in this server. I have many features, and more are"
                                            "coming.")
        em.add_field(name="XP", value="Being active on the server can get you XP. XP can get you to rank up, unlocking "
                                      "exclusive channels and commands.")
        em.add_field(name="Get a Code?", value="Did you get a code when you were invited? Run /claim <code> to claim"
                                               "the code and get XP. Make sure to do it quick, if you take too long,"
                                               "you'll never be able to claim a code again.")
        await member.send(embed=em)

        # Give child role to member
        await member.add_roles(member.guild.get_role(1021965016976605316))

