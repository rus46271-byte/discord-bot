import discord
from groq import Groq

# 1. API 키와 디스코드 토큰을 넣으세요. (큰따옴표 "" 유지!)
GROQ_API_KEY = "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"
DISCORD_TOKEN = "MTUzNjY2OTQ1NDMyNTM4NzMxNA.Gwasa0.fWzxRJ5W2A97xh3zkoLkDSGL6yHPY5Bi0TCopQ"

# Groq 클라이언트 생성
groq_client = Groq(api_key=GROQ_API_KEY)

# 디스코드 봇 권한 설정
intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    print(f'🤖 {bot.user.name} 이 그록처럼 그록조록 켜졌습니다!')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith('!'):
        user_text = message.content[1:].strip()
        
        if not user_text:
            await message.channel.send("질문 내용을 입력해 주세요! (예: `! 안녕?`)")
            return

        async with message.channel.typing():
            try:
                # Groq의 대표 고성능 오픈소스 모델 Llama-3.3-70b 호출
                chat_completion = groq_client.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": user_text,
                        }
                    ],
                    model="llama-3.3-70b-versatile",
                )
                
                answer = chat_completion.choices[0].message.content
                await message.channel.send(answer)

            except Exception as e:
                await message.channel.send(f"오류가 발생했습니다: {e}")

bot.run(DISCORD_TOKEN)