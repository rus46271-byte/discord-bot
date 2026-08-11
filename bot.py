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
    print(f'🤖 {bot.user.name} 이 대화 기억 모드로 켜졌습니다!')

@bot.event
async def on_message(message):
    # 봇 자신이 보낸 메시지는 무시
    if message.author == bot.user:
        return

    # '!' 로 시작하는 질문만 처리
    if message.content.startswith('!'):
        user_text = message.content[1:].strip()
        
        if not user_text:
            await message.channel.send("질문 내용을 입력해 주세요! (예: `!안녕`)")
            return

        async with message.channel.typing():
            try:
                # 1. 해당 채널의 최근 메시지 10개를 불러옵니다.
                raw_messages = []
                async for msg in message.channel.history(limit=10):
                    raw_messages.append(msg)
                
                # 과거 메시지부터 순서대로 정리 (오래된 것 -> 최근 것)
                raw_messages.reverse()

                # 2. AI에게 넘겨줄 대화 기록(messages) 리스트 작성
                messages_for_ai = [
                    {
                        "role": "system", 
                        "content": "너는 친절하고 재미있는 디스코드 AI 그록이야. 이전 대화 맥락을 잘 기억하고 답변해줘.답변할 때는 절대 이상한 한자를 쓰지 말고, 오직 자연스러운 한국어로만 대답해. 불필요한 단어를 덧붙이지 마. 영어도 가급적 사용하지말고 미소녀처럼 행동해"
                    }
                ]

                for msg in raw_messages:
                    # 봇이 작성한 답변인 경우
                    if msg.author == bot.user:
                        messages_for_ai.append({"role": "assistant", "content": msg.content})
                    # 사용자가 '!' 명령어 형태로 보낸 질문인 경우
                    elif msg.content.startswith('!'):
                        clean_content = msg.content[1:].strip()
                        if clean_content:
                            messages_for_ai.append({"role": "user", "content": clean_content})

                # 3. 누적된 대화 기록 전체를 Groq AI에 전달
                chat_completion = groq_client.chat.completions.create(
                    messages=messages_for_ai,
                    model="llama-3.3-70b-versatile",
                )
                
                answer = chat_completion.choices[0].message.content
                await message.channel.send(answer)

            except Exception as e:
                await message.channel.send(f"오류가 발생했습니다: {e}")

bot.run(DISCORD_TOKEN)