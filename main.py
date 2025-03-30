import chainlit as cl
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

cl.run(host="0.0.0.0", port=8000)

# 시스템 프롬프트 정의
SYSTEM_PROMPTS = {
    "ox": (
        "당신은 한국 중학교 영어 교과 내용을 기반으로 문법 OX 문제를 출제하는 AI입니다. "
        "입력받은 문법 항목에 맞춰 총 10개의 OX 문제를 만들고, 정답과 해설은 맨 마지막에 모아서 쓰세요. "
        "문장은 실제 시험처럼 자연스러운 수준이어야 하며, 한국 중학생이 푸는 문제라고 생각하세요."
    ),
    "fill": (
        "당신은 한국 중학교 영어 교과 내용을 기반으로 문법 빈칸 채우기 문제를 출제하는 AI입니다. "
        "입력받은 문법 항목에 맞춰 총 10개의 문항을 생성하고, 각 문항에는 빈칸을 하나만 만듭니다. 정답과 해설은 맨 마지막에 모아서 쓰세요. "
        "문장은 일상적이고 자연스러워야 하며, 한국 중학생 수준이어야 합니다."
    )
}

# 상태 저장용 세션 변수 키
MODE_KEY = "selected_mode"

@cl.on_chat_start
async def start():
    await cl.Message(
        content=(
            "안녕하세요, 문법 문제 출제 도우미입니다! 👋\n"
            "어떤 유형의 문제를 원하시나요?\n\n"
            "- `OX`\n"
            "- `빈칸`\n\n"
            "문제 유형을 입력해주세요!"
        )
    ).send()

@cl.on_message
async def main(message: cl.Message):
    selected_mode = cl.user_session.get(MODE_KEY)

    if selected_mode is None:
        user_choice = message.content.strip().lower()
        if "ox" in user_choice:
            cl.user_session.set(MODE_KEY, "ox")
            await cl.Message("⭕️ OX 문제를 선택하셨습니다! 생성할 문법 항목을 입력해주세요.").send()
        elif "빈칸" in user_choice or "fill" in user_choice:
            cl.user_session.set(MODE_KEY, "fill")
            await cl.Message("📝 빈칸 채우기 문제를 선택하셨습니다! 생성할 문법 항목을 입력해주세요.").send()
        else:
            await cl.Message("죄송해요, 문제 유형을 이해하지 못했어요. 'OX' 또는 '빈칸'을 입력해주세요.").send()
        return

    # 문제 생성 파트
    system_prompt = SYSTEM_PROMPTS[selected_mode]
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message.content}
        ]
    )
    reply = response.choices[0].message.content.strip()
    await cl.Message(content=reply).send()

    # 계속 이어질 수 있도록 문법 항목 재입력 유도
    await cl.Message(content="다른 문법 항목으로 또 문제를 생성하시겠어요? 계속 입력해주세요 ✍️\n또는 '종료'라고 입력하시면 종료됩니다.").send()

    if message.content.strip().lower() in ["종료", "quit", "exit"]:
        cl.user_session.set(MODE_KEY, None)
        