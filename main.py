import discord
from discord.ext import commands
import json, random, os, asyncio, time, traceback
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("MTQ4NjI1NzI4NzkxOTE3MzY2Mg.GJVNn7.rq9iZVajgtoF0Q3uD0ogH9Pjb6jc0xqTxXsJ3U")

if not TOKEN:
    print("⚠️ TOKEN chưa set")
    exit()

# ================= CONFIG =================
WIN_GIF = "https://media.giphy.com/media/111ebonMs90YLu/giphy.gif"
LOSE_GIF = "https://media.giphy.com/media/3o7TKr3nzbh5WgCFxe/giphy.gif"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ================= DATA =================
def load():
    if not os.path.exists("users.json"):
        with open("users.json","w") as f:
            json.dump({},f)
    try:
        with open("users.json") as f:
            return json.load(f)
    except:
        return {}

def save():
    with open("users.json","w") as f:
        json.dump(users,f,indent=4)

users = load()

def get_user(uid):
    uid=str(uid)
    if uid not in users:
        users[uid]={"money":1000,"bank":0,"last_daily":0,"last_work":0}
    return users[uid]

def parse_bet(u,bet):
    try:
        if isinstance(bet,str):
            if bet.lower()=="all":
                return max(1,u["money"])
            bet=int(bet)
        return max(1,bet)
    except:
        return 0

# ================= COOLDOWN =================
cooldowns={}
def check_cd(uid,sec=2):
    now=time.time()
    if uid in cooldowns and now-cooldowns[uid]<sec:
        return False
    cooldowns[uid]=now
    return True

# ================= BASIC =================
@bot.command()
async def bal(ctx):
    u=get_user(ctx.author.id)
    await ctx.send(f"💰 {u['money']:,} | 🏦 {u['bank']:,}")

# ================= HELP =================
@bot.command()
async def help(ctx):
    await ctx.send("""
📜 LỆNH:

💰 TIỀN:
!bal !pay !deposit !withdraw

🎁 FARM:
!daily !work

🎮 GAME:
!slot <bet>
!taixiu <bet> tài/xỉu
!baucu <bet> <con>
!flip <bet> sấp/ngửa
!bomb <bet> sống/nổ
!bj <bet>
!hit !stand
!baccarat <bet> player/banker/tie

🔥 tip: dùng "all"
""")

# ================= PAY =================
@bot.command()
async def pay(ctx,member:discord.Member,amount:int):
    u=get_user(ctx.author.id)
    if amount<=0 or u["money"]<amount or member.id==ctx.author.id:
        return await ctx.send("❌")

    await ctx.send("Xác nhận? yes/no")
    def check(m): return m.author==ctx.author

    try:
        msg=await bot.wait_for("message",timeout=10,check=check)
    except:
        return await ctx.send("⏳")

    if msg.content!="yes":
        return await ctx.send("❌")

    r=get_user(member.id)
    u["money"]-=amount
    r["money"]+=amount
    save()
    await ctx.send("✅")

# ================= BANK =================
@bot.command()
async def deposit(ctx,amount):
    u=get_user(ctx.author.id)
    amount=parse_bet(u,amount)
    if u["money"]<amount:
        return await ctx.send("❌")
    u["money"]-=amount
    u["bank"]+=amount
    save()
    await ctx.send(f"🏦 +{amount}")

@bot.command()
async def withdraw(ctx,amount):
    u=get_user(ctx.author.id)
    amount=parse_bet(u,amount)
    if u["bank"]<amount:
        return await ctx.send("❌")
    u["bank"]-=amount
    u["money"]+=amount
    save()
    await ctx.send(f"💸 +{amount}")

# ================= DAILY =================
@bot.command()
async def daily(ctx):
    u=get_user(ctx.author.id)
    if time.time()-u["last_daily"]<86400:
        return await ctx.send("⏳")
    r=random.randint(500,1500)
    u["money"]+=r
    u["last_daily"]=time.time()
    save()
    await ctx.send(f"🎁 +{r}")

# ================= WORK =================
@bot.command()
async def work(ctx):
    u=get_user(ctx.author.id)
    if time.time()-u["last_work"]<20:
        return await ctx.send("⏳")
    jobs=["Dev","Driver","Streamer","Hacker","Banker"]
    earn=random.randint(200,1000)
    u["money"]+=earn
    u["last_work"]=time.time()
    save()
    await ctx.send(f"💼 {random.choice(jobs)} +{earn}")

# ================= FLIP =================
@bot.command()
async def flip(ctx,bet,choice:str):
    if not check_cd(ctx.author.id): return await ctx.send("⏳")
    u=get_user(ctx.author.id)
    bet=parse_bet(u,bet)

    if u["money"]<bet or choice not in ["sấp","ngửa"]:
        return await ctx.send("❌")

    msg=await ctx.send("🪙...")
    for _ in range(6):
        await msg.edit(content=random.choice(["🪙","💿"]))
        await asyncio.sleep(0.1)

    result=random.choice(["sấp","ngửa"])
    if choice==result:
        u["money"]+=bet
        gif=WIN_GIF
        text="🎉"
    else:
        u["money"]-=bet
        gif=LOSE_GIF
        text="💀"

    u["money"]=max(0,u["money"])
    save()

    embed=discord.Embed(title="🪙 FLIP",description=f"{result}\n{text}")
    embed.set_image(url=gif)
    await msg.edit(content=None,embed=embed)

# ================= SLOT =================
@bot.command()
async def slot(ctx,bet):
    if not check_cd(ctx.author.id): return await ctx.send("⏳")
    u=get_user(ctx.author.id)
    bet=parse_bet(u,bet)

    if u["money"]<bet:
        return await ctx.send("❌")

    icons=["🍒","🍋","🍉","7️⃣","💎"]
    msg=await ctx.send("🎰...")

    for _ in range(8):
        await msg.edit(content=" | ".join(random.choices(icons,k=3)))
        await asyncio.sleep(0.1)

    r=[random.choice(icons) for _ in range(3)]

    if r[0]==r[1]==r[2]:
        win=bet*8
        u["money"]+=win
        gif=WIN_GIF
        text=f"🎉 +{win}"
    else:
        u["money"]-=bet
        gif=LOSE_GIF
        text="💀"

    u["money"]=max(0,u["money"])
    save()

    embed=discord.Embed(title="🎰 SLOT",description=f"{' | '.join(r)}\n{text}")
    embed.set_image(url=gif)
    await msg.edit(content=None,embed=embed)

# ================= TAIXIU =================
@bot.command()
async def taixiu(ctx,bet,choice:str):
    if not check_cd(ctx.author.id): return await ctx.send("⏳")
    u=get_user(ctx.author.id)
    bet=parse_bet(u,bet)

    emoji=["⚀","⚁","⚂","⚃","⚄","⚅"]
    msg=await ctx.send("🎲...")

    for i in range(10):
        await msg.edit(content=" ".join(random.choices(emoji,k=3)))
        await asyncio.sleep(0.08+i*0.01)

    dice=[random.randint(1,6) for _ in range(3)]
    total=sum(dice)
    result="tài" if total>=11 else "xỉu"
    visual=" ".join([emoji[d-1] for d in dice])

    if choice==result:
        u["money"]+=bet
        gif=WIN_GIF
        text="🎉"
    else:
        u["money"]-=bet
        gif=LOSE_GIF
        text="💀"

    u["money"]=max(0,u["money"])
    save()

    embed=discord.Embed(title="🎲 TÀI XỈU",
        description=f"{visual}\n{total} → {result}\n{text}")
    embed.set_image(url=gif)

    await msg.edit(content=None,embed=embed)

# ================= BAUCU =================
@bot.command()
async def baucu(ctx,bet,choice:str):
    if not check_cd(ctx.author.id): return await ctx.send("⏳")
    u=get_user(ctx.author.id)
    bet=parse_bet(u,bet)

    animals=["nai","bầu","gà","cá","cua","tôm"]
    icons={"nai":"🦌","bầu":"🍐","gà":"🐓","cá":"🐟","cua":"🦀","tôm":"🦐"}

    if choice not in animals or u["money"]<bet:
        return await ctx.send("❌")

    msg=await ctx.send("🎲...")

    for _ in range(10):
        fake=[icons[random.choice(animals)] for _ in range(3)]
        await msg.edit(content=" | ".join(fake))
        await asyncio.sleep(0.1)

    dice=[random.choice(animals) for _ in range(3)]
    visual=" | ".join([icons[d] for d in dice])
    count=dice.count(choice)

    if count>0:
        win=bet*count
        u["money"]+=win
        gif=WIN_GIF
        text=f"🎉 x{count} +{win}"
    else:
        u["money"]-=bet
        gif=LOSE_GIF
        text="💀"

    u["money"]=max(0,u["money"])
    save()

    embed=discord.Embed(title="🎲 BẦU CUA",description=f"{visual}\n{text}")
    embed.set_image(url=gif)

    await msg.edit(content=None,embed=embed)

# ================= BOMB =================
@bot.command()
async def bomb(ctx,bet,choice:str):
    if not check_cd(ctx.author.id): return await ctx.send("⏳")
    u=get_user(ctx.author.id)
    bet=parse_bet(u,bet)

    if choice not in ["sống","nổ"] or u["money"]<bet:
        return await ctx.send("❌")

    msg=await ctx.send("💣...")

    for _ in range(6):
        await msg.edit(content=random.choice(["💣 .","💣 ..","💣 💥 ?"]))
        await asyncio.sleep(0.3)

    outcome=random.choice(["sống","nổ","nổ"])

    if choice==outcome:
        win=bet*2 if outcome=="sống" else bet*3
        u["money"]+=win
        gif=WIN_GIF
        text=f"🎉 {outcome} +{win}"
    else:
        u["money"]-=bet
        gif=LOSE_GIF
        text=f"💀 {outcome}"

    u["money"]=max(0,u["money"])
    save()

    embed=discord.Embed(title="💣 BOMB",description=text)
    embed.set_image(url=gif)

    await msg.edit(content=None,embed=embed)

# ================= ERROR =================
@bot.event
async def on_command_error(ctx,error):
    print(error)
    traceback.print_exc()
    await ctx.send("⚠️ lỗi")

# ================= READY =================
@bot.event
async def on_ready():
    print(f"{bot.user} ONLINE")

bot.run(TOKEN)
