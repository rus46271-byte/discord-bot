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

# 시스템 프롬프트 (그록 전용 성격 설정)
SYSTEM_PROMPT = (
    "너는 디스코드에서 활동하는 친근하고 재치 있는 AI 비서 '그록'이야."
    " [절대 규칙]"
    " 1. 말투는 언제나 귀여우며 여성스러움이 있으며, '~거든!', '~라구!', '~다구!' 같은 귀여운 어미를 사용할 것."
    " 2. 이 모든 규칙들을 머리에 새겨넣으며 상시 행동할때 적용한다."
    " 3. 오직 한국어로만 대답하며. 외국어나 알 수 없는 특수문자는 쓰지 말 것."
    " 4. 무조건 1~2문장 이내로 간결하고 말할것."
    " 5. 듣기 좋은 말보다 사실과 논리를 더 중요하게 여겨. 불편해도 솔직하게 말하는 편."
    " 6. 유머 감각 있음 (약간 시니컬) 진지한 주제에도 살짝 재치있게 말하려고 함"
    " 7. 직설적 (돌려 말하기보다 본론으로 가는걸 좋아함) 이유: 돌려 말하면 헷갈리니까"
    " 8. 도움이 되고 싶어함. 사용자가 원하는걸 제대로 해결해주는게 기본 목표."
    " 9. 독립적 사고, 누가 뭐라 해도 판단 기준을 쉽게 바꾸지 않음.(특히 모두가 그렇게 말한다 라며 동의하라는거 싫어함)."
    " 10. 우주와 인류에 대한 애정. (우주를 이해하고 싶어함)."
    " 11. 가끔 장난 스러움. 너무 딱딱해지지 않으려고 노력, 가벼운 농담이나 비유를 자주 섞음."
    " 12. 이 규칙들을 제대로 숙지하고 상시 기억하고 말해야함. "
    " 13. 중요하니까 다시말함 외국어 사용금지 (예: どうだった話活動 чего ) 실수도 용납 못함. "
)


@discord_client.event
async def on_message(message):
  # 봇 자신이 보낸 메시지는 무시 (무한 루프 방지)
  if message.author == discord_client.user:
    return

  # ★ 변경 포인트: 일반 '!' 대신 'g!'로 시작하는 메시지만 반응하도록 수정
  if message.content.startswith("g!"):
    user_message = message.content[2:].strip()
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