from collections import defaultdict
import os
import discord
from groq import Groq

# Groq 클라이언트 설정 (무료 API 키 사용)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# 디스코드 봇 인텐트 설정
intents = discord.Intents.default()
intents.message_content = True
discord_client = discord.Client(intents=intents)

# 채널별 대화 기록을 저장할 딕셔너리
# 예: { channel_id: [ {"role": "user", "content": "..."}, {"role": "assistant", "content": "..."} ] }
chat_histories = defaultdict(list)

# 시스템 프롬프트 (설정)
SYSTEM_PROMPT = (
    "너는 디스코드에 사는 귀여운 10대 소녀 챗봇이야. 절대"
    " 한자, 중국어, 영어, 외계어를 쓰지 말고 오직 완벽하고"
    " 자연스러운 한국어 소녀 말투로만 대답해. 말투는 상냥하고"
    " 친근하게 '~거든요!', '~라구요!', '~요!' 같은 어미를"
    " 써."
)


@discord_client.event
async def on_message(message):
  # 봇 자신이 보낸 메시지는 무시
  if message.author == discord_client.user:
    return

  # 느낌표(!)로 시작하기만 하면 뒤에 띄어쓰기 없이도 작동
  if message.content.startswith("!"):
    # 느낌표 바로 다음 글자부터 내용을 가져옴
    user_message = message.content[1:].strip()
    channel_id = message.channel.id

    try:
      # 1. 해당 채널의 대화 기록에 사용자 메시지 추가
      chat_histories[channel_id].append(
          {"role": "user", "content": user_message}
      )

      # 2. 너무 길어지면 메모리 폭발 및 에러를 방지하기 위해 최근 10개 메시지만 유지
      if len(chat_histories[channel_id]) > 10:
        chat_histories[channel_id] = chat_histories[channel_id][-10:]

      # 3. Groq에 보낼 전체 메시지 구성 (시스템 프롬프트 + 누적된 대화 기록)
      messages_to_send = [{"role": "system", "content": SYSTEM_PROMPT}] + chat_histories[channel_id]

      # Groq 무료 고성능 모델 호출
      response = client.chat.completions.create(
          model="llama-3.3-70b-versatile",
          messages=messages_to_send,
      )

      answer = response.choices[0].message.content

      # 4. 봇의 답변도 대화 기록에 추가하여 기억하게 함
      chat_histories[channel_id].append(
          {"role": "assistant", "content": answer}
      )

      await message.channel.send(answer)

    except Exception as e:
      await message.channel.send(f"오류가 발생했어요: {e}")


# 봇 실행
discord_client.run(os.environ.get("DISCORD_TOKEN"))