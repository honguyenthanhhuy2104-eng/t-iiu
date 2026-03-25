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
        users[uid] = {
            "money": 1000,
            "bank": 0,
            "last_daily": 0,
            "last_work": 0
        }
    return users[uid]

# ================= GIF =================
WIN_GIF = "https://media.giphy.com/media/111ebonMs90YLu/giphy.gif"
LOSE_GIF = "https://media.giphy.com/media/ISOckXUybVfQ4/giphy.gif"

# ================= BAL =================
@bot.command()
async def bal(ctx, member: discord.Member = None):
    member = member or ctx.author
    u = get_user(member.id)
    total = u["money"] + u["bank"]

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
    await ctx.send(f"🏦 gửi {amount:,}")

@bot.command()
async def withdraw(ctx, amount: int):
    u = get_user(ctx.author.id)
    if amount <= 0 or u["bank"] < amount:
        return await ctx.send("❌ thiếu bank")

    u["bank"] -= amount
    u["money"] += amount
    save()
    await ctx.send(f"💸 rút {amount:,}")

# ================= DAILY =================
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

    await ctx.send(f"🎁 +{reward:,}")

# ================= WORK (UPGRADE) =================
@bot.command()
async def work(ctx):
    u = get_user(ctx.author.id)
    now = time.time()

    if now - u["last_work"] < 20:
        return await ctx.send("⏳ Nghỉ 20s")

    jobs = [
        ("👨‍💻 Dev",300,800),
        ("🚗 Tài xế",200,600),
        ("🎮 Streamer",400,1000),
        ("🎨 Designer",250,700)
    ]

    job = random.choice(jobs)
    earn = random.randint(job[1], job[2])

    if random.random() < 0.1:
        earn *= 2
        status = "🔥 CRITICAL"
    elif random.random() < 0.1:
        earn = int(earn * 0.3)
        status = "💀 FAIL"
    else:
        status = "✅"

    u["money"] += earn
    u["last_work"] = now
    save()

    await ctx.send(f"{job[0]} | +{earn:,} | {status}")

# ================= SLOT =================
@bot.command()
async def slot(ctx, bet: int):
    u = get_user(ctx.author.id)
    if bet <= 0 or u["money"] < bet:
        return await ctx.send("❌ invalid bet")

    icons = ["🍒","🍋","🍉","7️⃣","💎"]
    msg = await ctx.send("🎰 Quay...")

    r = ["❓","❓","❓"]

    for i in range(12):
        await msg.edit(content="🎰 " + " | ".join(random.choices(icons,k=3)))
        await asyncio.sleep(0.07)

    for i in range(3):
        r[i] = random.choice(icons)
        await msg.edit(content="🎰 " + " | ".join(r))
        await asyncio.sleep(0.3)

    if r[0]==r[1]==r[2]:
        win = bet*10
        u["money"]+=win
        result="🎉 JACKPOT"
        gif=WIN_GIF
    else:
        u["money"]-=bet
        result="💀 LOSE"
        gif=LOSE_GIF

    save()

    embed=discord.Embed(title=result,description=" | ".join(r))
    embed.set_image(url=gif)
    await msg.edit(content=None,embed=embed)

# ================= TAIXIU =================
@bot.command()
async def taixiu(ctx, bet:int, choice:str):
    u=get_user(ctx.author.id)
    if bet<=0 or u["money"]<bet:
        return await ctx.send("❌")

    msg=await ctx.send("🎲 lắc...")

    for _ in range(10):
        await msg.edit(content=f"🎲 {[random.randint(1,6) for _ in range(3)]}")
        await asyncio.sleep(0.1)

    dice=[random.randint(1,6) for _ in range(3)]
    total=sum(dice)
    result="tài" if total>=11 else "xỉu"

    if choice.lower()==result:
        u["money"]+=bet
        text="🎉 WIN"
        gif=WIN_GIF
    else:
        u["money"]-=bet
        text="💀 LOSE"
        gif=LOSE_GIF

    save()

    embed=discord.Embed(title=f"{dice}={total}",description=text)
    embed.set_image(url=gif)
    await msg.edit(content=None,embed=embed)

# ================= FLIP =================
@bot.command()
async def flip(ctx, bet:int):
    u=get_user(ctx.author.id)
    if bet<=0 or u["money"]<bet:
        return await ctx.send("❌")

    msg=await ctx.send("🪙...")

    for _ in range(5):
        await msg.edit(content=random.choice(["Heads","Tails"]))
        await asyncio.sleep(0.2)

    if random.choice([True,False]):
        u["money"]+=bet
        text="WIN"
        gif=WIN_GIF
    else:
        u["money"]-=bet
        text="LOSE"
        gif=LOSE_GIF

    save()

    embed=discord.Embed(title=text)
    embed.set_image(url=gif)
    await msg.edit(content=None,embed=embed)

# ================= BLACKJACK =================
@bot.command()
async def blackjack(ctx, bet:int):
    u=get_user(ctx.author.id)
    if bet<=0 or u["money"]<bet:
        return await ctx.send("❌")

    player=random.randint(16,21)
    dealer=random.randint(15,21)

    if player>dealer:
        u["money"]+=bet
        text="WIN"
        gif=WIN_GIF
    else:
        u["money"]-=bet
        text="LOSE"
        gif=LOSE_GIF

    save()

    embed=discord.Embed(title=f"{player} vs {dealer}",description=text)
    embed.set_image(url=gif)
    await ctx.send(embed=embed)

# ================= BAUCU =================
@bot.command()
async def baucu(ctx, bet:int):
    u=get_user(ctx.author.id)
    animals=["nai","bầu","gà","cá","cua","tôm"]

    if u["money"]<bet:
        return await ctx.send("❌")

    if random.choice(animals)==random.choice(animals):
        u["money"]+=bet*3
        text="WIN x3"
        gif=WIN_GIF
    else:
        u["money"]-=bet
        text="LOSE"
        gif=LOSE_GIF

    save()

    embed=discord.Embed(title="🎲 Bầu cua",description=text)
    embed.set_image(url=gif)
    await ctx.send(embed=embed)

# ================= BOMB =================
@bot.command()
async def bomb(ctx, bet:int):
    u=get_user(ctx.author.id)

    if u["money"]<bet:
        return await ctx.send("❌")

    if random.randint(1,3)==1:
        u["money"]+=bet*4
        text="💥 Sống"
        gif=WIN_GIF
    else:
        u["money"]-=bet
        text="💀 Nổ"
        gif=LOSE_GIF

    save()

    embed=discord.Embed(title=text)
    embed.set_image(url=gif)
    await ctx.send(embed=embed)

# ================= TOP =================
@bot.command()
async def top(ctx):
    sorted_users = sorted(users.items(), key=lambda x: x[1]["money"]+x[1]["bank"], reverse=True)

    msg="🏆 TOP\n"
    for i,(uid,data) in enumerate(sorted_users[:5]):
        user=await bot.fetch_user(int(uid))
        msg+=f"{i+1}. {user.name} - {data['money']+data['bank']:,}\n"

    await ctx.send(msg)

# ================= MENU =================
@bot.command()
async def game(ctx):
    await ctx.send("🎮 slot | taixiu | flip | blackjack | baucu | bomb")

@bot.command()
async def helpgame(ctx):
    await ctx.send("bal, pay, deposit, withdraw, daily, work, top, game")

# ================= READY =================
@bot.event
async def on_ready():
    print(f"{bot.user} ONLINE FINAL")

bot.run(TOKEN)
