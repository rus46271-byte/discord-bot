import os
import discord
from openai import OpenAI

# xAI Grok API 클라이언트 설정 (OpenAI 호환 방식)
client = OpenAI(
    api_key=os.environ.get("XAI_API_KEY"),
    base_url="https://api.x.ai/v1",
)

# 봇 기본 설정
intents = discord.Intents.default()
intents.message_content = True
client_discord = discord.Client(intents=intents)


@client_discord.event
async def on_message(message):
  if message.author == client_discord.user:
    return

  # 봇을 부르는 명령어 조건 (예: !질문 이나 멘션 등 본인 코드에 맞게 수정)
  if message.content.startswith("!질문"):
    user_message = message.content[3:].strip()

    try:
      # xAI의 Grok 모델 호출
      response = client.chat.completions.create(
          model="grok-beta",  # xAI의 Grok 모델명
          messages=[
              {
                  "role": "system",
                  "content": (
                      "너는 디스코드에 머무는 봇이야. 항상 자연스럽고 친근한 한국어로만"
                      " 대답하되 너는 귀여운 10대 소녀야 항상 상냥한 말투에, 귀여운 소녀를 모방해"
                  ),
              },
              {"role": "user", "content": user_message},
          ],
      )

      answer = response.choices[0].message.content
      await message.channel.send(answer)

    except Exception as e:
      await message.channel.send(f"오류가 발생했습니다: {e}")


# 토큰은 본인의 디스코드 봇 토큰으로 유지
client_discord.run(os.environ.get("DISCORD_BOT_TOKEN"))