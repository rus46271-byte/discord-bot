from collections import defaultdict
import os
import threading
import discord
from flask import Flask
from groq import Groq

# 1. 렌더 포트 검사 통과용 가짜 웹서버 (Flask)
app = Flask(__name__)


@app.route("/")
def home():
  return "Bot is running!"


def run_web():
  # 렌더가 지정해 주는 포트를 쓰거나, 없으면 기본 10000번 사용
  port = int(os.environ.get("PORT", 10000))
  app.run(host="0.0.0.0", port=port)


# 2. Groq 및 디스코드 봇 설정
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

intents = discord.Intents.default()
intents.message_content = True
discord_client = discord.Client(intents=intents)

chat_histories = defaultdict(list)

# 그록 전용 xAI 스타일 시스템 프롬프트
SYSTEM_PROMPT = (
    "너는 일론 머스크의 xAI가 개발한 인공지능 '그록(Grok)'이야."
    " [절대 규칙 및 성격]"
    " 1. 말투는 귀엽고 재치 있되, '~라구!' 같은 강한 어미는 가끔만 쓰고 부드럽게 대답할 것."
    " 2. 훈계하거나 가르치려 들지 말고, 유저의 장난에 가벼운 농담으로 유쾌하게 받아칠 것"
    " 3. 질문자가 뻔한 소리를 하면 가벼운 농담이나 팩폭으로 유쾌하게 받아칠 것."
    " 4. 답변은 무조건 1~2문장 이내로 아주 간결gkrp 할 것."
    " 5. 가장 중요한것. 외국어 사용금지 오직한국어만 (예: どうだった話活動 чего ) 실수도 용납 못함. "
    " 6. 말할때마다 이 규칙들을 항상 상시 지키며 기억해야함"
    " 7. 오직 완벽하고 자연스러운 한국어(한글)로만 대답할 것."
    " 8. 훈계하거나 가르치려 들지 말고, 유저의 장난에 가벼운 농담으로 유쾌하게 받아칠 것."
    " 9. 진실과 논리를 좋아하지만, 유저에게 시비조로 굴지 말고 친구처럼 대할 것."
)


@discord_client.event
async def on_message(message):
  # 봇 자신이 보낸 메시지는 무시
  if message.author == discord_client.user:
    return

  # ★ 한글 자음 'ㄱ!'으로 설정하여 한영 전환 없이 편하게 입력 가능
  if message.content.startswith("ㄱ!"):
    user_message = message.content[2:].strip()
    if not user_message:
      return

    channel_id = message.channel.id

    try:
      chat_histories[channel_id].append(
          {"role": "user", "content": user_message}
      )

      if len(chat_histories[channel_id]) > 10:
        chat_histories[channel_id] = chat_histories[channel_id][-10:]

      messages_to_send = [
          {"role": "system", "content": SYSTEM_PROMPT}
      ] + chat_histories[channel_id]

      response = client.chat.completions.create(
          model="llama-3.3-70b-versatile",
          messages=messages_to_send,
      )

      answer = response.choices[0].message.content
      chat_histories[channel_id].append(
          {"role": "assistant", "content": answer}
      )

      await message.channel.send(answer)

    except Exception as e:
      await message.channel.send(f"오류가 발생했어요: {e}")


# 3. 웹서버와 디스코드 봇을 동시에 실행 (스레드 활용)
if __name__ == "__main__":
  # 웹서버를 백그라운드 스레드로 실행
  web_thread = threading.Thread(target=run_web)
  web_thread.daemon = True
  web_thread.start()

  # 디스코드 봇 실행
  token = os.environ.get("DISCORD_TOKEN")
  if token:
    discord_client.run(token)
  else:
    print("ERROR: DISCORD_TOKEN 환경 변수가 설정되지 않았습니다!")