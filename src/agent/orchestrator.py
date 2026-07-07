"""
Agent 오케스트레이터.

Claude의 tool-use(함수 호출) 기능을 이용해
- 정보 질문 -> search_hr_documents 도구로 RAG 검색 -> 근거 기반 답변
- 액션 요청 -> get_leave_balance / apply_leave / get_attendance_summary 호출
두 경로를 하나의 에이전트 루프에서 자동으로 판단해 처리합니다.

세션별 대화 히스토리를 메모리에 보관해 멀티턴 대화를 지원합니다.
(운영 환경에서는 세션 저장소를 Redis 등 외부 스토리지로 교체하는 것을 권장합니다.)
"""
import json

import anthropic

from src.agent.prompts import AGENT_SYSTEM_PROMPT
from src.config import ANTHROPIC_API_KEY, CLAUDE_MODEL
from src.rag.retriever import Retriever
from src.tools.hr_system import TOOL_REGISTRY

MAX_TOOL_ITERATIONS = 4

TOOLS = [
    {
        "name": "search_hr_documents",
        "description": (
            "사내 규정·복지 문서에서 관련 내용을 검색합니다. "
            "정보성 질문(휴가/복지/근태 규정 등)에는 항상 이 도구를 먼저 사용하세요."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string", "description": "검색할 질문 또는 키워드"}},
            "required": ["query"],
        },
    },
    {
        "name": "get_leave_balance",
        "description": "직원의 잔여 연차 일수를 조회합니다.",
        "input_schema": {
            "type": "object",
            "properties": {"employee_id": {"type": "string", "description": "직원 ID"}},
            "required": ["employee_id"],
        },
    },
    {
        "name": "apply_leave",
        "description": "휴가 신청을 접수합니다.",
        "input_schema": {
            "type": "object",
            "properties": {
                "employee_id": {"type": "string", "description": "직원 ID"},
                "start_date": {"type": "string", "description": "휴가 시작일 (YYYY-MM-DD)"},
                "end_date": {"type": "string", "description": "휴가 종료일 (YYYY-MM-DD)"},
            },
            "required": ["employee_id", "start_date", "end_date"],
        },
    },
    {
        "name": "get_attendance_summary",
        "description": "이번 달 근태 요약(지각 횟수, 재택 일수 등)을 조회합니다.",
        "input_schema": {
            "type": "object",
            "properties": {"employee_id": {"type": "string", "description": "직원 ID"}},
            "required": ["employee_id"],
        },
    },
]


class HRAgent:
    def __init__(self) -> None:
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        self.retriever = Retriever()
        # session_id -> 메시지 히스토리 (데모용 인메모리 저장소)
        self.sessions: dict[str, list] = {}

    def _run_tool(self, name: str, tool_input: dict) -> dict:
        if name == "search_hr_documents":
            hits = self.retriever.search(tool_input["query"])
            return {"results": hits}

        fn = TOOL_REGISTRY.get(name)
        if fn is None:
            return {"error": f"알 수 없는 도구입니다: {name}"}
        return fn(**tool_input)

    def chat(self, session_id: str, user_message: str) -> dict:
        """사용자 메시지를 받아 에이전트 응답을 반환합니다.

        반환 형식: {"answer": str}
        """
        history = self.sessions.setdefault(session_id, [])
        history.append({"role": "user", "content": user_message})

        for _ in range(MAX_TOOL_ITERATIONS):
            response = self.client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=1024,
                system=AGENT_SYSTEM_PROMPT,
                tools=TOOLS,
                messages=history,
            )

            tool_use_blocks = [b for b in response.content if b.type == "tool_use"]
            history.append({"role": "assistant", "content": response.content})

            if not tool_use_blocks:
                answer = "\n".join(b.text for b in response.content if b.type == "text")
                return {"answer": answer}

            tool_results = []
            for block in tool_use_blocks:
                result = self._run_tool(block.name, block.input)
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result, ensure_ascii=False),
                    }
                )
            history.append({"role": "user", "content": tool_results})

        return {"answer": "요청을 처리하는 데 필요한 단계가 너무 많아 중단했습니다. 다시 시도해주세요."}
