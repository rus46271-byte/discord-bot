from collections import defaultdict
import os
import discord
from groq import Groq

# Groq 클라이언트 설정 (환경 변수에서 API 키를 가져옴)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# 디스코드 봇 인텐트 설정
intents = discord.Intents.default()
intents.message_content = True
discord_client = discord.Client(intents=intents)

# 채널별 대화 기록 저장 딕셔너리
chat_histories = defaultdict(list)

# 시스템 프롬프트 (외국어/외계어 방지 및 소녀 말투)
SYSTEM_PROMPT = (
    "너는 디스코드에 사는 귀여운 10대 소녀 챗봇이야."
    " 절대 한자, 중국어, 영어, 러시아어, 알 수 없는 외계어를"
    " 쓰지 말고 오직 완벽하고 자연스러운 한국어(한글)로만"
    " 대답해. 말투는 상냥하고 친근하게 '~거든요!',"
    " '~라구요!', '~요!' 같은 어미를 써."
)


@discord_client.event
async def on_message(message):
  # 봇 자신이 보낸 메시지는 무시 (무한 루프 방지)
  if message.author == discord_client.user:
    return

  # 느낌표(!)로 시작하는 메시지만 반응
  if message.content.startswith("!"):
    user_message = message.content[1:].strip()
    if not user_message:
      return

    channel_id = message.channel.id

    try:
      # 1. 대화 기록에 유저 메시지 추가
      chat_histories[channel_id].append(
          {"role": "user", "content": user_message}
      )

      # 2. 최근 10개 메시지만 유지하여 에러 방지
      if len(chat_histories[channel_id]) > 10:
        chat_histories[channel_id] = chat_histories[channel_id][-10:]

      # 3. Groq API 호출 데이터 구성
      messages_to_send = [
          {"role": "system", "content": SYSTEM_PROMPT}
      ] + chat_histories[channel_id]

      response = client.chat.completions.create(
          model="llama-3.3-70b-versatile",
          messages=messages_to_send,
      )

      answer = response.choices[0].message.content

      # 4. 봇의 답변도 기억에 추가
      chat_histories[channel_id].append(
          {"role": "assistant", "content": answer}
      )

      await message.channel.send(answer)

    except Exception as e:
      await message.channel.send(f"오류가 발생했어요: {e}")


# 봇 실행 (토큰 확인)
token = os.environ.get("DISCORD_TOKEN")
if token:
  discord_client.run(token)
else:
  print("ERROR: DISCORD_TOKEN 환경 변수가 설정되지 않았습니다!")