import discord
from discord.ext import commands
from discord.ui import Button, View
import json
import os

# 봇의 Intents 설정
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

# 봇 설정
bot = commands.Bot(command_prefix="!", intents=intents)

# 사전예약 데이터 저장
예약_상태 = set()
사전예약_채널_ID = 1339631243146559508  # 🔥 사전예약 채널 ID
사전예약_결과_채널_ID = 123456789012345678  # 다른 서버에 정보를 보낼 채널 ID
쿠폰코드 = "welcomeluna"

# 메시지 ID 저장 파일
MESSAGE_FILE = "reservation_message.json"
예약_상태_FILE = "reservation_status.json"  # 사전예약 상태 저장 파일

# 📌 메시지 ID 저장/불러오기 함수
def save_message_id(message_id):
    with open(MESSAGE_FILE, "w") as f:
        json.dump({"message_id": message_id}, f)

def load_message_id():
    if os.path.exists(MESSAGE_FILE):
        with open(MESSAGE_FILE, "r") as f:
            data = json.load(f)
            return data.get("message_id", None)
    return None

# 📌 사전예약 상태 저장/불러오기 함수
def save_reservation_status():
    with open(예약_상태_FILE, "w") as f:
        json.dump(list(예약_상태), f)

def load_reservation_status():
    if os.path.exists(예약_상태_FILE):
        with open(예약_상태_FILE, "r") as f:
            data = json.load(f)
            return set(data)
    return set()

사전예약_메시지_ID = load_message_id()

# 📌 사전예약 메시지 업데이트 함수 (숫자만 변경)
async def update_reservation_message():
    global 사전예약_메시지_ID

    channel = bot.get_channel(사전예약_채널_ID)
    if not channel:
        print("❌ 오류: 사전예약 채널을 찾을 수 없습니다.")
        return

    embed = discord.Embed(
        title="📢 LUNA-RP", 
        description="안녕하세요! 루나서버입니다! 🎉\n\n서버 오픈 전날까지 사전예약을 하여 보상을 받을 수 있습니다!\n\n루나서버를 위해 아래의 버튼을 눌러 사전예약을 완료 해주세요! ", 
        color=0x00ff00
    )
    embed.add_field(name="현재 사전예약 인원", value=f"{len(예약_상태)}명", inline=False)
    embed.set_footer(text="LUNA-RP 서버에서의 즐거운 여행을 기대해주세요!")

    if 사전예약_메시지_ID:
        try:
            message = await channel.fetch_message(사전예약_메시지_ID)
            await message.edit(embed=embed, view=예약버튼())
            return
        except discord.NotFound:
            print("❌ 기존 사전예약 메시지를 찾을 수 없음. 새로 생성합니다.")

    # 메시지 새로 생성
    message = await channel.send(embed=embed, view=예약버튼())
    사전예약_메시지_ID = message.id
    save_message_id(사전예약_메시지_ID)


# 📌 예약 버튼 UI
class 예약버튼(View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label="사전예약", style=discord.ButtonStyle.green, custom_id="예약버튼")
    async def 예약(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user

        if user.id in 예약_상태:
            await interaction.response.send_message(
                f"""
**이미 사전 예약을 진행하셨습니다.**\n
**쿠폰코드:** ||{쿠폰코드}||\n
-# 인게임에서 /쿠폰을 사용하여 쿠폰 등록이 가능합니다!
""",
                ephemeral=True
            )
            return

        예약_상태.add(user.id)
        save_reservation_status()  # 사전예약 상태 저장

        # 다른 서버에 정보 보내기
        다른_서버 = bot.get_guild(1334184724297416735)  # 대상 서버의 ID
        if 다른_서버:
            채널 = 다른_서버.get_channel(1339694506638835713)
            if 채널:
                await 채널.send(
                    f"사전예약 완료! {user.mention} ({user.name}) 님이 사전예약을 진행하셨습니다."
                )

        await interaction.response.send_message(
            f"""
{user.mention}님, **사전예약이 완료되었습니다!** 🎉\n
**쿠폰코드:** ||{쿠폰코드}||\n
-# 인게임에서 /쿠폰을 사용하여 쿠폰 등록이 가능합니다!
""",
            ephemeral=True
        )

        await update_reservation_message()


# 📌 봇 실행되면 기존 메시지 검색 및 업데이트
@bot.event
async def on_ready():
    print(f"{bot.user}가 연결되었습니다!")

    # 사전예약 상태 불러오기
    global 예약_상태
    예약_상태 = load_reservation_status()

    channel = bot.get_channel(사전예약_채널_ID)
    if channel:
        async for message in channel.history(limit=10):  # 최근 10개 메시지 검색
            if "LUNA-RP" in message.content:
                global 사전예약_메시지_ID
                사전예약_메시지_ID = message.id
                save_message_id(1339631243146559508)
                break

    await update_reservation_message()


# 📌 봇 실행 (토큰 추가)
bot.run("MTMzOTYzNjg1MTk5NjEwMjcxNg.GMoM8T.YUPdDgxXbFdxGwXvd2Zx09ZvHmN9tRHdQkhKDs")
