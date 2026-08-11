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
    print(f'🤖 {bot.user.name} 이 대화 기억 모드로 완벽히 켜졌습니다!')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # 메시지가 '!'로 시작하는지 확인
    if message.content.startswith('!'):
        user_text = message.content[1:].strip()
        
        if not user_text:
            await message.channel.send("질문 내용을 입력해 주세요! (예: `!안녕`)")
            return

        async with message.channel.typing():
            try:
                # 최근 메시지 15개를 읽어옴
                raw_messages = []
                async for msg in message.channel.history(limit=15):
                    raw_messages.append(msg)
                
                raw_messages.reverse() # 오래된 순서대로 정렬

                # AI 프롬프트 및 대화 기록 구성
                messages_for_ai = [
                    {
                        "role": "system", 
                        "content": "너는 디스코드 AI 도우미야. 반드시 한국어로만 자연스럽고 친절하게 답변해줘. 이전 대화 기록과 맥락을 잘 파악해서 기억해줘."
                    }
                ]

                for msg in raw_messages:
                    if msg.author == bot.user:
                        # 봇의 이전 답변 추가
                        if msg.content:
                            messages_for_ai.append({"role": "assistant", "content": msg.content})
                    elif msg.content.startswith('!'):
                        # 사용자의 '!' 질문 추가 (띄어쓰기 보완)
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