import discord
from discord.ext import commands
import json, random, os, asyncio
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
        users[uid] = {"money": 1000}
    return users[uid]

# ================= GIF =================

WIN_GIF = "https://media.giphy.com/media/111ebonMs90YLu/giphy.gif"
LOSE_GIF = "https://media.giphy.com/media/ISOckXUybVfQ4/giphy.gif"

# ================= MENU =================

@bot.command()
async def game(ctx):
    embed = discord.Embed(title="🎮 DANH SÁCH GAME", color=0x00ffcc)
    embed.add_field(name="🎰 Slot", value="!slot <tiền>", inline=False)
    embed.add_field(name="🎲 Tài xỉu", value="!taixiu <tiền> <tài/xỉu>", inline=False)
    embed.add_field(name="🪙 Flip", value="!flip <tiền>", inline=False)
    embed.add_field(name="🎯 Roll", value="!roll <tiền>", inline=False)
    embed.add_field(name="💣 Bomb", value="!bomb <tiền>", inline=False)
    await ctx.send(embed=embed)

# ================= SLOT =================

@bot.command()
async def slot(ctx, bet: int):
    u = get_user(ctx.author.id)
    if bet <= 0 or u["money"] < bet:
        return await ctx.send("❌ invalid bet")

    icons = ["🍒","🍋","🍉","7️⃣","💎"]
    msg = await ctx.send("🎰 Đang quay...")

    r = ["❓","❓","❓"]

    # quay animation
    for i in range(12):
        temp = [random.choice(icons) for _ in range(3)]
        await msg.edit(content="🎰 " + " | ".join(temp))
        await asyncio.sleep(0.08 + i*0.01)

    # dừng từng cột (fix không hiển thị 2 lần)
    for i in range(3):
        for _ in range(4):
            temp = r.copy()
            temp[i] = random.choice(icons)
            await msg.edit(content="🎰 " + " | ".join(temp))
            await asyncio.sleep(0.1)
        r[i] = random.choice(icons)
        await msg.edit(content="🎰 " + " | ".join(r))
        await asyncio.sleep(0.3)

    # kết quả
    if r[0] == r[1] == r[2]:
        win = bet * 10
        u["money"] += win
        result = f"💎 JACKPOT +{win}"
        gif = WIN_GIF
    else:
        u["money"] -= bet
        result = "💀 Thua"
        gif = LOSE_GIF

    save()

    embed = discord.Embed(title="🎰 KẾT QUẢ", description=result)
    embed.add_field(name="Reels", value=" | ".join(r))
    embed.set_image(url=gif)

    await msg.edit(content=None, embed=embed)

# ================= TAIXIU =================

@bot.command()
async def taixiu(ctx, bet: int, choice: str):
    u = get_user(ctx.author.id)
    if bet <= 0 or u["money"] < bet:
        return await ctx.send("❌ invalid bet")

    msg = await ctx.send("🎲 Đang lắc...")

    # animation lắc
    for i in range(12):
        fake = [random.randint(1,6) for _ in range(3)]
        await msg.edit(content=f"🎲 {fake}")
        await asyncio.sleep(0.06 + i*0.01)

    await msg.edit(content="🎲 Mở bát...")
    await asyncio.sleep(0.8)

    dice = [random.randint(1,6) for _ in range(3)]
    total = sum(dice)
    result = "tài" if total >= 11 else "xỉu"

    if choice.lower() == result:
        u["money"] += bet
        text = "🎉 WIN"
        gif = WIN_GIF
    else:
        u["money"] -= bet
        text = "💀 LOSE"
        gif = LOSE_GIF

    save()

    embed = discord.Embed(title=f"🎲 {dice} = {total}", description=text)
    embed.set_image(url=gif)

    await msg.edit(content=None, embed=embed)

# ================= READY =================

@bot.event
async def on_ready():
    print(f"{bot.user} FIXED & READY")

bot.run(TOKEN)
