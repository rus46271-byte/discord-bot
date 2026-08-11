import os
import discord
from discord import app_commands
from groq import Groq

# Render 환경변수에서 키와 토큰을 가져옵니다.
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")

groq_client = Groq(api_key=GROQ_API_KEY)

# 클라이언트 클래스 정의 (슬래시 명령어 커맨드트리 포함)
class MyClient(discord.Client):
    def __init__(self):
        # 메시지 읽기 권한(Message Content) 활성화
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # 디스코드에 슬래시 명령어 동기화 (등록)
        await self.tree.sync()

client = MyClient()

@client.event
async def on_ready():
    print(f'🤖 {client.user.name} 이 (느낌표 + 슬래시 통합모드)로 켜졌습니다!')

# ==========================================
# 1️⃣ [!] 느낌표 메세지 방식 (대화 기억 기능 포함)
# ==========================================
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!'):
        user_text = message.content[1:].strip()
        
        if not user_text:
            await message.channel.send("질문 내용을 입력해 주세요! (예: `!안녕`)")
            return

        async with message.channel.typing():
            try:
                # 최근 메시지 15개를 읽어와 대화 맥락 파악
                raw_messages = []
                async for msg in message.channel.history(limit=15):
                    raw_messages.append(msg)
                
                raw_messages.reverse()

                messages_for_ai = [
                    {
                        "role": "system", 
                        "content": (
                            "너는 디스코드 채널에서 사용자와 대화하는 친절하고 위트 있는 AI 봇이야. "
                            "이름은 '그록'이야. 반드시 자연스러운 한국어로 대답하고 이전 대화 기록을 기억해줘."
                        )
                    }
                ]

                for msg in raw_messages:
                    if msg.author == client.user:
                        if msg.content:
                            messages_for_ai.append({"role": "assistant", "content": msg.content})
                    elif msg.content.startswith('!'):
                        query_text = msg.content[1:].strip()
                        if query_text:
                            messages_for_ai.append({"role": "user", "content": query_text})

                chat_completion = groq_client.chat.completions.create(
                    messages=messages_for_ai,
                    model="llama-3.3-70b-versatile",
                )
                
                answer = chat_completion.choices[0].message.content
                await message.channel.send(answer)

            except Exception as e:
                await message.channel.send(f"오류가 발생했습니다: {e}")

# ==========================================
# 2️⃣ [/도움말] 슬래시 명령어
# ==========================================
@client.tree.command(name="도움말", description="그록 AI 봇 사용 방법을 확인합니다.")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🤖 그록 AI 봇 사용 안내",
        description="그록 봇과 대화하는 방법입니다!",
        color=discord.Color.blue()
    )
    embed.add_field(
        name="1. `!질문` 방식 (대화 맥락 기억 O)",
        value="`!안녕`, `!내 이름이 뭐라고?` 처럼 앞에 `!`를 붙이고 질문하면 이전 대화를 기억하며 대답합니다.",
        inline=False
    )
    embed.add_field(
        name="2. `/질문` 방식",
        value="`/질문 내용:안녕하세요` 명령어로 일회성 빠른 질문을 보낼 수 있습니다.",
        inline=False
    )
    embed.set_footer(text="스마트한 AI 도우미 그록")
    
    await interaction.response.send_message(embed=embed)

# ==========================================
# 3️⃣ [/질문] 슬래시 명령어
# ==========================================
@client.tree.command(name="질문", description="그록 AI에게 바로 질문합니다.")
@app_commands.describe(내용="AI에게 물어볼 내용을 입력하세요")
async def ask_command(interaction: discord.Interaction, 내용: str):
    await interaction.response.defer()

    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": "너는 디스코드 AI 도우미야. 한국어로 친절하게 대답해줘."},
                {"role": "user", "content": 내용}
            ],
            model="llama-3.3-70b-versatile",
        )
        answer = chat_completion.choices[0].message.content
        await interaction.followup.send(answer)

    except Exception as e:
        await interaction.followup.send(f"오류가 발생했습니다: {e}")

client.run(DISCORD_TOKEN)