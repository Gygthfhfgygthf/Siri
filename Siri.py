import ssl
import certifi
ssl._create_default_https_context = ssl.create_default_context(cafile=certifi.where())
import discord
from discord.ext import commands
from discord.utils import get
import os
import datetime
from dotenv import load_dotenv

load_dotenv()



# ─────────────────────────────────────────
#  SETUP
# ─────────────────────────────────────────

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ─────────────────────────────────────────
#  EVENTS
# ─────────────────────────────────────────

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching, name="the server"
    ))

@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name="general")
    if channel:
        await channel.send(f"👋 Welcome to the server, {member.mention}!")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if "hello" in message.content.lower():
        await message.channel.send(f"Hey {message.author.mention}!")
    await bot.process_commands(message)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You lack permission for this command.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Missing argument. Use `!help {ctx.command.name}` for usage.")
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send("❌ Member not found.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Invalid argument provided.")
    else:
        await ctx.send(f"❌ Error: {error}")

# ─────────────────────────────────────────
#  UTILITY COMMANDS
# ─────────────────────────────────────────

@bot.command(name="ping", help="Check bot latency.")
async def ping(ctx):
    await ctx.send(f"🏓 Pong! Latency: `{round(bot.latency * 1000)}ms`")

@bot.command(name="serverinfo", help="Display server information.")
async def serverinfo(ctx):
    guild = ctx.guild
    embed = discord.Embed(title=f"📊 {guild.name}", color=discord.Color.blurple())
    embed.add_field(name="Owner", value=guild.owner.mention)
    embed.add_field(name="Members", value=guild.member_count)
    embed.add_field(name="Channels", value=len(guild.channels))
    embed.add_field(name="Roles", value=len(guild.roles))
    embed.add_field(name="Created", value=guild.created_at.strftime("%b %d, %Y"))
    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
    await ctx.send(embed=embed)

@bot.command(name="userinfo", help="Display info about a user.")
async def userinfo(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title=f"👤 {member.display_name}", color=member.color)
    embed.add_field(name="Username", value=str(member))
    embed.add_field(name="ID", value=member.id)
    embed.add_field(name="Joined Server", value=member.joined_at.strftime("%b %d, %Y"))
    embed.add_field(name="Account Created", value=member.created_at.strftime("%b %d, %Y"))
    embed.add_field(name="Top Role", value=member.top_role.mention)
    embed.set_thumbnail(url=member.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command(name="say", help="Make the bot say something.")
@commands.has_permissions(manage_messages=True)
async def say(ctx, *, text: str):
    await ctx.message.delete()
    await ctx.send(text)

# ─────────────────────────────────────────
#  MESSAGING COMMANDS
# ─────────────────────────────────────────

@bot.command(name="dm", help="DM a user. Usage: !dm @user <message>")
@commands.has_permissions(administrator=True)
async def dm_user(ctx, member: discord.Member, *, message: str):
    try:
        await member.send(message)
        await ctx.send(f"✅ DM sent to {member.mention}.")
    except discord.Forbidden:
        await ctx.send("❌ Could not DM that user (DMs may be disabled).")

@bot.command(name="announce", help="Post an announcement embed.")
@commands.has_permissions(administrator=True)
async def announce(ctx, *, message: str):
    embed = discord.Embed(
        title="📢 Announcement",
        description=message,
        color=discord.Color.gold(),
        timestamp=datetime.datetime.utcnow()
    )
    embed.set_footer(text=f"Posted by {ctx.author.display_name}")
    await ctx.send(embed=embed)

# ─────────────────────────────────────────
#  MODERATION COMMANDS
# ─────────────────────────────────────────

@bot.command(name="kick", help="Kick a member. Usage: !kick @user [reason]")
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason: str = "No reason provided"):
    await member.kick(reason=reason)
    embed = discord.Embed(title="👢 Member Kicked", color=discord.Color.orange())
    embed.add_field(name="User", value=member.mention)
    embed.add_field(name="Moderator", value=ctx.author.mention)
    embed.add_field(name="Reason", value=reason, inline=False)
    await ctx.send(embed=embed)

@bot.command(name="ban", help="Ban a member. Usage: !ban @user [reason]")
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason: str = "No reason provided"):
    await member.ban(reason=reason)
    embed = discord.Embed(title="🔨 Member Banned", color=discord.Color.red())
    embed.add_field(name="User", value=member.mention)
    embed.add_field(name="Moderator", value=ctx.author.mention)
    embed.add_field(name="Reason", value=reason, inline=False)
    await ctx.send(embed=embed)

@bot.command(name="unban", help="Unban a user. Usage: !unban username#0000")
@commands.has_permissions(ban_members=True)
async def unban(ctx, *, username: str):
    banned = [entry async for entry in ctx.guild.bans()]
    for entry in banned:
        if str(entry.user) == username:
            await ctx.guild.unban(entry.user)
            await ctx.send(f"✅ Unbanned **{entry.user}**.")
            return
    await ctx.send("❌ User not found in ban list.")

@bot.command(name="mute", help="Mute a member. Usage: !mute @user [reason]")
@commands.has_permissions(moderate_members=True)
async def mute(ctx, member: discord.Member, *, reason: str = "No reason provided"):
    # Uses Discord's built-in timeout (mute) for 1 hour by default
    duration = datetime.timedelta(hours=1)
    await member.timeout(duration, reason=reason)
    embed = discord.Embed(title="🔇 Member Muted", color=discord.Color.dark_gray())
    embed.add_field(name="User", value=member.mention)
    embed.add_field(name="Duration", value="1 hour")
    embed.add_field(name="Moderator", value=ctx.author.mention)
    embed.add_field(name="Reason", value=reason, inline=False)
    await ctx.send(embed=embed)

@bot.command(name="unmute", help="Unmute a member. Usage: !unmute @user")
@commands.has_permissions(moderate_members=True)
async def unmute(ctx, member: discord.Member):
    await member.timeout(None)
    await ctx.send(f"✅ {member.mention} has been unmuted.")

@bot.command(name="warn", help="Warn a member. Usage: !warn @user <reason>")
@commands.has_permissions(manage_messages=True)
async def warn(ctx, member: discord.Member, *, reason: str):
    embed = discord.Embed(title="⚠️ Warning Issued", color=discord.Color.yellow())
    embed.add_field(name="User", value=member.mention)
    embed.add_field(name="Moderator", value=ctx.author.mention)
    embed.add_field(name="Reason", value=reason, inline=False)
    await ctx.send(embed=embed)
    try:
        await member.send(f"⚠️ You have been warned in **{ctx.guild.name}**.\nReason: {reason}")
    except discord.Forbidden:
        pass  # User has DMs disabled

@bot.command(name="clear", help="Delete messages. Usage: !clear [amount]")
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 5):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"🗑️ Deleted `{amount}` messages.", delete_after=3)

# ─────────────────────────────────────────
#  ADMIN / ROLE COMMANDS
# ─────────────────────────────────────────

@bot.command(name="addrole", help="Add a role to a member. Usage: !addrole @user <role>")
@commands.has_permissions(manage_roles=True)
async def addrole(ctx, member: discord.Member, *, role_name: str):
    role = discord.utils.get(ctx.guild.roles, name=role_name)
    if not role:
        await ctx.send("❌ Role not found.")
        return
    await member.add_roles(role)
    await ctx.send(f"✅ Added **{role.name}** to {member.mention}.")

@bot.command(name="removerole", help="Remove a role from a member. Usage: !removerole @user <role>")
@commands.has_permissions(manage_roles=True)
async def removerole(ctx, member: discord.Member, *, role_name: str):
    role = discord.utils.get(ctx.guild.roles, name=role_name)
    if not role:
        await ctx.send("❌ Role not found.")
        return
    await member.remove_roles(role)
    await ctx.send(f"✅ Removed **{role.name}** from {member.mention}.")

@bot.command(name="slowmode", help="Set channel slowmode. Usage: !slowmode <seconds>")
@commands.has_permissions(manage_channels=True)
async def slowmode(ctx, seconds: int):
    await ctx.channel.edit(slowmode_delay=seconds)
    await ctx.send(f"⏱️ Slowmode set to `{seconds}s` in {ctx.channel.mention}.")

@bot.command(name="lock", help="Lock the current channel.")
@commands.has_permissions(manage_channels=True)
async def lock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send("🔒 Channel locked.")

@bot.command(name="unlock", help="Unlock the current channel.")
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send("🔓 Channel unlocked.")

# ─────────────────────────────────────────
#  RUN
# ─────────────────────────────────────────

bot.run(os.getenv("DISCORD_TOKEN"))
