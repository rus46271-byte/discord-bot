import os
import discord
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("XAI_API_KEY"),
    base_url="https://api.x.ai/v1",
)

intents = discord.Intents.default()
intents.message_content = True
discord_client = discord.Client(intents=intents)


@discord_client.event
async def on_message(message):
  if message.author == discord_client.user:
    return

  # 느낌표(!)로 시작하고 바로 뒤에 띄어쓰기가 있는 경우를 처리
  if message.content.startswith("! "):
    user_message = message.content[2:].strip()

    try:
      response = client.chat.completions.create(
          model="grok-beta",
          messages=[
              {
                  "role": "system",
                  "content": (
                      "너는 디스코드에 사는 귀여운 10대 소녀 챗봇이야. 말투는"
                      " 상냥하고 친근하게 '~거든요!', '~라구요!', '~요!' 같은"
                      " 어미를 쓰고, 감정도 풍부하게 표현해. 절대 한자나 이상한"
                      " 외계어를 쓰지 말고 오직 자연스러운 한국어 소녀"
                      " 말투로만 대답해."
                  ),
              },
              {"role": "user", "content": user_message},
          ],
      )

      answer = response.choices[0].message.content
      await message.channel.send(answer)

    except Exception as e:
      await message.channel.send(f"오류가 발생했어요: {e}")


discord_client.run(os.environ.get("DISCORD_TOKEN"))