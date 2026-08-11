import os
import discord
from groq import Groq

# Render 환경변수에서 키와 토큰을 가져옵니다.
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")

groq_client = Groq(api_key=GROQ_API_KEY)

intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    print(f'🤖 {bot.user.name} 이 센스 만점 AI 모드로 켜졌습니다!')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # '!'로 시작하는 질문 처리
    if message.content.startswith('!'):
        user_text = message.content[1:].strip()
        
        if not user_text:
            await message.channel.send("질문 내용을 입력해 주세요! (예: `!안녕`)")
            return

        async with message.channel.typing():
            try:
                # 최근 메시지 15개를 읽어와 맥락 파악
                raw_messages = []
                async for msg in message.channel.history(limit=15):
                    raw_messages.append(msg)
                
                raw_messages.reverse() # 오래된 순서대로 정렬

                # 🔥 핵심: AI의 정체성과 규칙을 강력하게 정의
                messages_for_ai = [
                    {
                        "role": "system", 
                        "content": (
                            "너는 디스코드 채널에서 사용자와 대화하는 친절하고 위트 있는 AI 봇이야. "
                            "이름은 '그록'이야. "
                            "절대로 스타트렉이나 외계인 이야기 같은 엉뚱한 소리를 하지 마. 웃긴 얘기는 해도 됨 "
                            "반드시 자연스러운 한국어로 답변하고, 이전 대화 맥락과 사용자 이름을 잘 기억해줘."
                        )
                    }
                ]

                for msg in raw_messages:
                    if msg.author == bot.user:
                        if msg.content:
                            messages_for_ai.append({"role": "assistant", "content": msg.content})
                    elif msg.content.startswith('!'):
                        query_text = msg.content[1:].strip()
                        if query_text:
                            messages_for_ai.append({"role": "user", "content": query_text})

                # Groq API 호출
                chat_completion = groq_client.chat.completions.create(
                    messages=messages_for_ai,
                    model="llama-3.3-70b-versatile",
                )
                
                answer = chat_completion.choices[0].message.content
                await message.channel.send(answer)

            except Exception as e:
                await message.channel.send(f"오류가 발생했습니다: {e}")

bot.run(DISCORD_TOKEN)