import discord
from discord.ext import commands
import json, random, os, asyncio, time
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
        users[uid] = {"money": 1000, "bank": 0, "last_daily": 0, "last_work": 0}
    return users[uid]

# ================= GIF =================
WIN_GIF = "https://media.giphy.com/media/111ebonMs90YLu/giphy.gif"
LOSE_GIF = "https://media.giphy.com/media/ISOckXUybVfQ4/giphy.gif"

# ================= BAL =================
@bot.command()
async def bal(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author

    u = get_user(member.id)
    total = u.get("money", 0) + u.get("bank", 0)

    embed = discord.Embed(title=f"💰 {member.name}", color=0x00ffcc)
    embed.add_field(name="💵 Tiền", value=f"{u['money']:,}")
    embed.add_field(name="🏦 Bank", value=f"{u['bank']:,}")
    embed.add_field(name="💎 Tổng", value=f"{total:,}")

    if member.avatar:
        embed.set_thumbnail(url=member.avatar.url)

    await ctx.send(embed=embed)

# ================= PAY =================
@bot.command()
async def pay(ctx, member: discord.Member, amount: int):
    u = get_user(ctx.author.id)
    r = get_user(member.id)

    if amount <= 0 or u["money"] < amount:
        return await ctx.send("❌ Không đủ tiền")

    u["money"] -= amount
    r["money"] += amount
    save()

    await ctx.send(f"💸 {ctx.author.mention} → {member.mention} {amount:,}")

# ================= BANK =================
@bot.command()
async def deposit(ctx, amount: int):
    u = get_user(ctx.author.id)
    if amount <= 0 or u["money"] < amount:
        return await ctx.send("❌ thiếu tiền")

    u["money"] -= amount
    u["bank"] += amount
    save()

    await ctx.send(f"🏦 Đã gửi {amount:,}")

@bot.command()
async def withdraw(ctx, amount: int):
    u = get_user(ctx.author.id)
    if amount <= 0 or u["bank"] < amount:
        return await ctx.send("❌ thiếu bank")

    u["bank"] -= amount
    u["money"] += amount
    save()

    await ctx.send(f"💸 Rút {amount:,}")

# ================= DAILY =================
@bot.command()
async def daily(ctx):
    u = get_user(ctx.author.id)
    now = time.time()

    if now - u["last_daily"] < 86400:
        return await ctx.send("⏳ Chưa đến giờ daily")

    reward = random.randint(500, 1500)
    u["money"] += reward
    u["last_daily"] = now
    save()

    await ctx.send(f"🎁 Nhận {reward:,}")

# ================= WORK =================
@bot.command()
async def work(ctx):
    u = get_user(ctx.author.id)
    now = time.time()

    if now - u["last_work"] < 30:
        return await ctx.send("⏳ Nghỉ 30s")

    earn = random.randint(100, 600)
    u["money"] += earn
    u["last_work"] = now
    save()

    await ctx.send(f"🧑‍💼 +{earn:,}")

# ================= LEADERBOARD =================
@bot.command()
async def top(ctx):
    sorted_users = sorted(users.items(), key=lambda x: x[1]["money"] + x[1]["bank"], reverse=True)

    embed = discord.Embed(title="🏆 TOP GIÀU NHẤT", color=0xffd700)

    for i, (uid, data) in enumerate(sorted_users[:5]):
        user = await bot.fetch_user(int(uid))
        total = data["money"] + data["bank"]
        embed.add_field(name=f"#{i+1} {user.name}", value=f"{total:,}", inline=False)

    await ctx.send(embed=embed)

# ================= GAME MENU =================
@bot.command()
async def game(ctx):
    embed = discord.Embed(title="🎮 GAME", color=0x00ffcc)
    embed.add_field(name="🎰 Slot", value="!slot <tiền>")
    embed.add_field(name="🎲 Tài xỉu", value="!taixiu <tiền> <tài/xỉu>")
    embed.add_field(name="🪙 Flip", value="!flip <tiền>")
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

    for i in range(12):
        temp = [random.choice(icons) for _ in range(3)]
        await msg.edit(content="🎰 " + " | ".join(temp))
        await asyncio.sleep(0.08 + i*0.01)

    for i in range(3):
        for _ in range(4):
            temp = r.copy()
            temp[i] = random.choice(icons)
            await msg.edit(content="🎰 " + " | ".join(temp))
            await asyncio.sleep(0.1)
        r[i] = random.choice(icons)
        await msg.edit(content="🎰 " + " | ".join(r))
        await asyncio.sleep(0.3)

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

# ================= FLIP =================
@bot.command()
async def flip(ctx, bet: int):
    u = get_user(ctx.author.id)
    if bet <= 0 or u["money"] < bet:
        return await ctx.send("❌ invalid bet")

    msg = await ctx.send("🪙 Đang tung...")

    for _ in range(6):
        await msg.edit(content=random.choice(["🪙 Heads...", "🪙 Tails..."]))
        await asyncio.sleep(0.2)

    win = random.choice([True, False])

    if win:
        u["money"] += bet
        text = "🎉 WIN"
        gif = WIN_GIF
    else:
        u["money"] -= bet
        text = "💀 LOSE"
        gif = LOSE_GIF

    save()

    embed = discord.Embed(title="🪙 Kết quả", description=text)
    embed.set_image(url=gif)

    await msg.edit(content=None, embed=embed)

# ================= READY =================
@bot.event
async def on_ready():
    print(f"{bot.user} FULL CASINO ONLINE")

bot.run(TOKEN)
