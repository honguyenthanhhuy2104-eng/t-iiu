import discord
from discord.ext import commands
import json, random, os, time, asyncio
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# ================= DATA =================

def load():
    try:
        with open("users.json", "r") as f:
            return json.load(f)
    except:
        return {}


def save():
    with open("users.json", "w") as f:
        json.dump(users, f, indent=4)

users = load()


def get_user(uid):
    uid = str(uid)
    if uid not in users:
        users[uid] = {"money": 1000, "bank": 0}
    return users[uid]

# ================= EFFECT HELPERS =================

async def loading_bar(msg, steps=10, delay=0.2):
    for i in range(steps):
        bar = "█" * i + "░" * (steps - i)
        await msg.edit(content=f"[{bar}]")
        await asyncio.sleep(delay)

async def spin_effect(msg, frames, delay=0.1):
    for f in frames:
        await msg.edit(content=f)
        await asyncio.sleep(delay)

# ================= BAL =================

@bot.command()
async def bal(ctx):
    u = get_user(ctx.author.id)
    embed = discord.Embed(title="💰 ACCOUNT", color=0x00ffcc)
    embed.add_field(name="💵 Money", value=u['money'])
    embed.add_field(name="🏦 Bank", value=u['bank'])
    await ctx.send(embed=embed)

# ================= FLIP =================

@bot.command()
async def flip(ctx, bet: int):
    u = get_user(ctx.author.id)
    if bet <= 0 or u["money"] < bet:
        return await ctx.send("❌ invalid bet")

    msg = await ctx.send("🪙 starting...")

    await loading_bar(msg)

    frames = ["🪙","🔄","🪙","🔄","🪙","✨"]
    await spin_effect(msg, frames, 0.2)

    win = random.choice([True, False])
    if win:
        u["money"] += bet
        text = "🎉 WIN"
    else:
        u["money"] -= bet
        text = "💀 LOSE"

    save()
    await msg.edit(content=text)

# ================= SLOT =================

@bot.command()
async def slot(ctx, bet: int):
    u = get_user(ctx.author.id)
    if bet <= 0 or u["money"] < bet:
        return await ctx.send("❌ invalid bet")

    icons = ["🍒","🍋","🍉","7️⃣","💎"]
    msg = await ctx.send("🎰 loading...")

    await loading_bar(msg)

    speed = 0.05
    for i in range(15):
        r = [random.choice(icons) for _ in range(3)]
        await msg.edit(content="🎰 " + " ".join(r))
        await asyncio.sleep(speed)
        speed += 0.01

    if r[0] == r[1] == r[2]:
        win = bet * 7
        u["money"] += win
        text = f"💎 JACKPOT +{win}"
    else:
        u["money"] -= bet
        text = "💀 lose"

    save()
    await msg.edit(content=f"🎰 {' '.join(r)}\n{text}")

# ================= TAIXIU =================

@bot.command()
async def taixiu(ctx, bet: int, choice: str):
    u = get_user(ctx.author.id)
    if bet <= 0 or u["money"] < bet:
        return await ctx.send("❌ invalid bet")

    msg = await ctx.send("🎲 loading...")

    await loading_bar(msg)

    for i in range(10):
        fake = [random.randint(1,6) for _ in range(3)]
        await msg.edit(content=f"🎲 {fake}")
        await asyncio.sleep(0.1 + i*0.02)

    dice = [random.randint(1,6) for _ in range(3)]
    total = sum(dice)
    result = "tài" if total >= 11 else "xỉu"

    if choice.lower() == result:
        u["money"] += bet
        text = "🎉 WIN"
    else:
        u["money"] -= bet
        text = "💀 LOSE"

    save()
    await msg.edit(content=f"🎲 {dice} = {total}\n{text}")

# ================= ROLL =================

@bot.command()
async def roll(ctx, bet: int):
    u = get_user(ctx.author.id)
    if bet <= 0 or u["money"] < bet:
        return await ctx.send("❌ invalid bet")

    msg = await ctx.send("🎯 loading...")

    await loading_bar(msg)

    n = 0
    for i in range(15):
        n = random.randint(1,100)
        await msg.edit(content=f"🎯 {n}")
        await asyncio.sleep(0.05 + i*0.01)

    if n > 80:
        u["money"] += bet*2
        text = "🔥 BIG WIN"
    elif n > 40:
        text = "😐 draw"
    else:
        u["money"] -= bet
        text = "💀 lose"

    save()
    await msg.edit(content=f"🎯 {n}\n{text}")

# ================= GUESS =================

@bot.command()
async def guess(ctx, bet: int, number: int):
    u = get_user(ctx.author.id)
    if bet <= 0 or u["money"] < bet:
        return await ctx.send("❌ invalid bet")

    msg = await ctx.send("🔢 thinking...")

    await loading_bar(msg)

    for i in range(8):
        await msg.edit(content=f"🔢 {random.randint(1,5)}")
        await asyncio.sleep(0.15)

    secret = random.randint(1,5)

    if number == secret:
        u["money"] += bet*3
        text = "🎉 WIN"
    else:
        u["money"] -= bet
        text = "💀 LOSE"

    save()
    await msg.edit(content=f"🔢 {secret}\n{text}")

# ================= BOMB =================

@bot.command()
async def bomb(ctx, bet: int):
    u = get_user(ctx.author.id)
    if bet <= 0 or u["money"] < bet:
        return await ctx.send("❌ invalid bet")

    msg = await ctx.send("💣 preparing...")

    await loading_bar(msg)

    wires = ["🟥","🟦","🟩","🟨"]

    for i in range(10):
        await msg.edit(content=" ".join(random.sample(wires,4)))
        await asyncio.sleep(0.1 + i*0.02)

    if random.randint(1,4) == 1:
        u["money"] += bet*4
        text = "💥 SAFE"
    else:
        u["money"] -= bet
        text = "💀 BOOM"

    save()
    await msg.edit(content=text)

# ================= READY =================

@bot.event
async def on_ready():
    print(f"{bot.user} online PRO MAX")

bot.run(TOKEN)
