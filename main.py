import discord
from discord.ext import commands
import json
import random
import os
import time
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
        users[uid] = {
            "money": 1000,
            "bank": 0,
            "last_daily": 0,
            "last_work": 0
        }
    return users[uid]

# ================= BASIC =================
@bot.command()
async def bal(ctx):
    u = get_user(ctx.author.id)
    await ctx.send(f"💰 {u['money']} | 🏦 {u['bank']}")

@bot.command()
async def pay(ctx, member: discord.Member, amount: int):
    u = get_user(ctx.author.id)
    r = get_user(member.id)

    if u["money"] < amount:
        return await ctx.send("❌ Không đủ tiền")

    u["money"] -= amount
    r["money"] += amount
    save()

    await ctx.send(f"💸 {ctx.author.mention} → {member.mention} {amount}")

# ================= DAILY / WORK =================
@bot.command()
async def daily(ctx):
    u = get_user(ctx.author.id)
    now = time.time()

    if now - u["last_daily"] < 86400:
        return await ctx.send("⏳ Đợi daily")

    reward = random.randint(500, 1500)
    u["money"] += reward
    u["last_daily"] = now
    save()

    await ctx.send(f"🎁 +{reward}")

@bot.command()
async def work(ctx):
    u = get_user(ctx.author.id)
    now = time.time()

    if now - u["last_work"] < 30:
        return await ctx.send("⏳ nghỉ 30s")

    earn = random.randint(100, 600)
    u["money"] += earn
    u["last_work"] = now
    save()

    await ctx.send(f"🧑‍💼 +{earn}")

# ================= BANK =================
@bot.command()
async def deposit(ctx, amount: int):
    u = get_user(ctx.author.id)

    if u["money"] < amount:
        return await ctx.send("❌ thiếu tiền")

    u["money"] -= amount
    u["bank"] += amount
    save()

    await ctx.send("🏦 gửi thành công")

@bot.command()
async def withdraw(ctx, amount: int):
    u = get_user(ctx.author.id)

    if u["bank"] < amount:
        return await ctx.send("❌ thiếu bank")

    u["bank"] -= amount
    u["money"] += amount
    save()

    await ctx.send("💸 rút thành công")

# ================= CASINO =================
@bot.command()
async def flip(ctx, bet: int):
    u = get_user(ctx.author.id)
    if u["money"] < bet:
        return await ctx.send("❌ thiếu tiền")

    if random.choice([True, False]):
        u["money"] += bet
        msg = "🎉 win"
    else:
        u["money"] -= bet
        msg = "💀 lose"

    save()
    await ctx.send(msg)

@bot.command()
async def taixiu(ctx, bet: int, choice: str):
    u = get_user(ctx.author.id)

    if u["money"] < bet:
        return await ctx.send("❌ thiếu tiền")

    dice = [random.randint(1, 6) for _ in range(3)]
    total = sum(dice)
    result = "tài" if total >= 11 else "xỉu"

    if choice == result:
        u["money"] += bet
        msg = "🎉 win"
    else:
        u["money"] -= bet
        msg = "💀 lose"

    save()
    await ctx.send(f"{msg} {dice} = {total}")

@bot.command()
async def baucu(ctx, bet: int):
    u = get_user(ctx.author.id)
    animals = ["nai", "bầu", "gà", "cá", "cua", "tôm"]

    if u["money"] < bet:
        return await ctx.send("❌ thiếu tiền")

    result = random.choice(animals)

    if random.choice(animals) == result:
        u["money"] += bet * 3
        msg = "🎉 win x3"
    else:
        u["money"] -= bet
        msg = "💀 lose"

    save()
    await ctx.send(f"{msg} {result}")

@bot.command()
async def slot(ctx, bet: int):
    u = get_user(ctx.author.id)
    icons = ["🍒", "🍋", "🍉", "7️⃣"]

    if u["money"] < bet:
        return await ctx.send("❌ thiếu tiền")

    r = [random.choice(icons) for _ in range(3)]

    if r[0] == r[1] == r[2]:
        win = bet * 5
        u["money"] += win
        msg = "🎰 JACKPOT"
    else:
        u["money"] -= bet
        msg = "💀 lose"

    save()
    await ctx.send(f"{msg} {' '.join(r)}")

# ================= MINI GAMES =================
@bot.command()
async def guess(ctx, bet: int, number: int):
    u = get_user(ctx.author.id)

    if u["money"] < bet:
        return await ctx.send("❌ thiếu tiền")

    secret = random.randint(1, 5)

    if number == secret:
        u["money"] += bet * 3
        msg = "🎉 win"
    else:
        u["money"] -= bet
        msg = "💀 lose"

    save()
    await ctx.send(f"{msg} ({secret})")

@bot.command()
async def roll(ctx, bet: int):
    u = get_user(ctx.author.id)

    if u["money"] < bet:
        return await ctx.send("❌ thiếu tiền")

    n = random.randint(1, 100)

    if n > 80:
        u["money"] += bet * 2
        msg = "🔥 big win"
    elif n > 40:
        msg = "😐 neutral"
    else:
        u["money"] -= bet
        msg = "💀 lose"

    save()
    await ctx.send(f"{msg} {n}")

@bot.command()
async def bomb(ctx, bet: int):
    u = get_user(ctx.author.id)

    if u["money"] < bet:
        return await ctx.send("❌ thiếu tiền")

    if random.randint(1, 3) == 1:
        u["money"] += bet * 4
        msg = "💥 survive win"
    else:
        u["money"] -= bet
        msg = "💣 boom lose"

    save()
    await ctx.send(msg)

# ================= LEADERBOARD =================
@bot.command()
async def top(ctx):
    sorted_users = sorted(users.items(), key=lambda x: x[1]["money"], reverse=True)

    msg = "🏆 TOP:\n"
    for i, (uid, data) in enumerate(sorted_users[:5]):
        user = await bot.fetch_user(int(uid))
        msg += f"{i+1}. {user.name} - {data['money']}\n"

    await ctx.send(msg)

# ================= READY =================
@bot.event
async def on_ready():
    print(f"{bot.user} online")

bot.run(TOKEN)