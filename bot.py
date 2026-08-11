import os
import discord
from groq import Groq

# Render의 환경 변수(Environment)에서 키와 토큰을 가져옵니다.
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")

groq_client = Groq(api_key=GROQ_API_KEY)

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
            await message.channel.send("질문 내용을 입력해 주세요! (예: `!안녕`)")
            return

        async with message.channel.typing():
            try:
                chat_completion = groq_client.chat.completions.create(
                    messages=[
                        {"role": "user", "content": user_text}
                    ],
                    model="llama-3.3-70b-versatile",
                )
                answer = chat_completion.choices[0].message.content
                await message.channel.send(answer)

            except Exception as e:
                await message.channel.send(f"오류가 발생했습니다: {e}")

bot.run(DISCORD_TOKEN)