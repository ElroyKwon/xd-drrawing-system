"""액션 제안(propose_*) — 대화형 write의 '제안' 단계. 8000을 mutate하지 않는다.

라벨(시트번호·이슈제목)→id 해소는 tools.py의 READ 경로(HTTP GET)만 쓴다. 여기서
반환하는 pending_action은 프론트 확인 카드용 스펙일 뿐 실행이 아니다(휴먼인더루프).
"""
from __future__ import annotations

import uuid

import tools

VALID_STATUSES = {"열림", "진행중", "답변됨", "닫힘"}


def _new_id() -> str:
    return uuid.uuid4().hex[:12]


def propose_create_issue(project: str, args: dict) -> dict:
    title = (args.get("title") or "").strip()
    sheet_ref = (args.get("sheet_ref") or "").strip()
    file_id = sheet_id = None
    target_label = None
    if sheet_ref:
        # list_sheets(READ)에서 번호/제목 부분일치로 시트 해소.
        res = tools.list_sheets(project)
        for s in res.get("sheets") or []:
            hay = f"{s.get('number','')} {s.get('title','')}"
            if sheet_ref.lower() in hay.lower():
                sheet_id = s.get("sheet_id")
                file_id = s.get("file_id")
                target_label = s.get("number") or s.get("title")
                break
    return {
        "action_id": _new_id(),
        "type": "create_issue",
        "summary": f"이슈 생성: {title}" + (f" · {target_label}" if target_label else " · (전역)"),
        "params": {
            "title": title,
            "type": args.get("type") or "설계 검토",
            "category": args.get("category") or "",
            "assignee": args.get("assignee") or "",
            "description": args.get("description") or "",
            "status": args.get("status") if args.get("status") in VALID_STATUSES else "열림",
            "file_id": file_id,
            "sheet_id": sheet_id,
        },
        "target_label": target_label,
    }


def propose_change_issue_status(project: str, args: dict) -> dict:
    ref = (args.get("issue_ref") or "").strip()
    to_status = args.get("to_status") if args.get("to_status") in VALID_STATUSES else None
    issue_id = None
    issue_title = None
    res = tools.list_issues(project)
    for it in res.get("issues") or []:
        if ref and (ref == it.get("issue_id") or ref.lower() in (it.get("title") or "").lower()):
            issue_id = it.get("issue_id")
            issue_title = it.get("title")
            break
    return {
        "action_id": _new_id(),
        "type": "change_issue_status",
        "summary": f"이슈 상태변경: {issue_title or ref} → {to_status or '(상태 미지정)'}",
        "params": {"issue_id": issue_id, "issue_title": issue_title, "to_status": to_status},
        "target_label": issue_title,
    }


def propose_create_task(project: str, args: dict) -> dict:
    title = (args.get("title") or "").strip()
    return {
        "action_id": _new_id(),
        "type": "create_task",
        "summary": f"작업 생성: {title}",
        "params": {
            "title": title,
            "assignee": args.get("assignee") or "",
            "status": args.get("status") or "할 일",
            "priority": args.get("priority") or "보통",
            "due_date": args.get("due_date") or "",
            "description": args.get("description") or "",
        },
        "target_label": None,
    }
