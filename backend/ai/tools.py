"""대표 읽기툴 2종 (S8.0): search, list_sheets. 오직 8000 HTTP로 그라운딩.

각 툴은 구조화 JSON + 안정 ID(sheet_id/file_id, 딥링크용)를 반환한다.
전체 툴 카탈로그(get_project_summary·get_sheet·list_issues·...)는 S8.2.
"""
from __future__ import annotations

from typing import Optional

from client import get


def search(project: str, query: str) -> dict:
    """GET /api/search — 시트·이슈·파일·폴더 교차 부분일치 검색 결과."""
    data = get("/api/search", params={"q": query, "project_name": project})
    return {
        "query": data.get("query", query),
        "sheets": data.get("sheets", []),
        "issues": data.get("issues", []),
        "files": data.get("files", []),
        "folders": data.get("folders", []),
        "truncated": data.get("truncated", False),
    }


def list_sheets(project: str, discipline: Optional[str] = None) -> dict:
    """GET /api/drawings — 완료 도면의 시트 목록(공종 코드 선택 필터).

    검색 라우트와 동일 매핑(sheet_number→number, sheet_title→title)으로 딥링크 ID 유지.
    """
    drawings = get("/api/drawings", params={"project_name": project})
    sheets = []
    for d in drawings:
        if d.get("conversion_status") != "completed":
            continue
        for s in d.get("sheets") or []:
            code = s.get("discipline_code") or "G"
            if discipline and code != discipline:
                continue
            number = s.get("sheet_number") or s.get("sheet_name") or d.get("filename")
            sheets.append({
                "sheet_id": s.get("sheet_id"),
                "file_id": d.get("file_id"),
                "number": number,
                "title": s.get("sheet_title") or d.get("filename"),
                "discipline_code": code,
                "discipline_label": s.get("discipline_label") or "",
            })
    return {"project": project, "count": len(sheets), "sheets": sheets}
