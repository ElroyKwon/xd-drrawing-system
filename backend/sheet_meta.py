"""시트 메타(번호·제목·공종) 휴리스틱 추출 (S2-a).

타이틀블록 텍스트 휴리스틱(메타프롬프트 03 Q3). PDF 페이지 텍스트/파일명에서
시트번호·제목·공종을 추정하고, 실패 시 폴백(파일명 → Page N)한다.

번호 추출 우선순위:
  1) 페이지 텍스트 후보가 파일명 접두 번호와 일치 → 고신뢰(파일명=번호인 단일도면)
  2) 라벨(DWG/SHEET/도면번호 등) 근처의 도면번호 후보
  3) 파일명에서 추출한 번호
  4) "Page N"
공종은 번호 접두 문자 매핑(E/A/M/P/S/C…), 미상은 "G"(기타).
"""
from __future__ import annotations

import os
import re

# 도면번호 후보: 영문 1~4 + (구분) + 숫자그룹(여러 단)
_CAND_RE = re.compile(r"\b([A-Za-z]{1,4}[-_ ]?\d{2,4}(?:[-_]\d{1,4}){0,2})\b")
# 파일명 선두 번호(언더스코어/공백 앞까지)
_FNAME_RE = re.compile(r"^([A-Za-z]{1,4}-?\d{2,4}(?:-\d{1,4}){0,2})")
# 번호 라벨 키워드(이 토큰 근처 후보를 우선)
_LABEL_RE = re.compile(r"(DWG\.?\s*NO|DRAWING\s*NO|SHEET\s*NO|도면\s*번호|도번)", re.IGNORECASE)

_DISCIPLINE = {
    "E": ("E", "E (전기)"), "EE": ("E", "E (전기)"), "EL": ("E", "E (전기)"),
    "A": ("A", "A (건축)"), "AR": ("A", "A (건축)"),
    "M": ("M", "M (기계)"), "ME": ("M", "M (기계)"),
    "P": ("P", "P (배관)"), "PL": ("P", "P (배관)"),
    "S": ("S", "S (구조)"), "ST": ("S", "S (구조)"),
    "C": ("C", "C (토목)"), "CV": ("C", "C (토목)"),
}


def _normalize(tok: str) -> str:
    return tok.strip().upper().replace("_", "-").replace(" ", "")


def _filename_number(filename: str) -> str | None:
    stem = os.path.splitext(os.path.basename(filename or ""))[0]
    m = _FNAME_RE.match(stem)
    return _normalize(m.group(1)) if m else None


def _candidates(text: str) -> list[str]:
    out = []
    for t in _CAND_RE.findall(text or ""):
        if any(c.isdigit() for c in t):
            out.append(_normalize(t))
    return out


def _near_label_number(text: str) -> str | None:
    """라벨(DWG/SHEET/도면번호) 근처의 도면번호 후보.

    라벨 다음 줄들엔 장비태그(TR-005 등) 노이즈가 섞일 수 있으므로,
    공종 접두가 인식되는 후보(진짜 도면번호)를 우선 채택하고 없으면 첫 후보로 폴백한다.
    """
    lines = (text or "").splitlines()
    for i, line in enumerate(lines):
        if _LABEL_RE.search(line):
            near: list[str] = []
            for j in (i, i + 1, i + 2):
                if 0 <= j < len(lines):
                    near.extend(_candidates(lines[j]))
            if near:
                known = [c for c in near if _discipline(c)[0] != "G"]
                return known[0] if known else near[0]
    return None


def _discipline(number: str) -> tuple[str, str]:
    m = re.match(r"([A-Za-z]{1,4})", number or "")
    if m:
        prefix = m.group(1).upper()
        if prefix in _DISCIPLINE:
            return _DISCIPLINE[prefix]
        # 첫 글자만으로 재시도
        if prefix[0] in _DISCIPLINE:
            return _DISCIPLINE[prefix[0]]
    return ("G", "G (기타)")


# 제목으로 잡으면 안 되는 타이틀블록 라벨어(누수 방지)
_TITLE_DENY = {"BUILDING NAME", "PROJECT TITLE", "DRAWING TITLE", "TITLE", "SCALE", "DATE",
               "DESCRIPTION", "REV", "NO", "SHEET", "도면명", "축척"}


def _title(text: str, filename: str) -> str:
    """파일명 stem을 우선 제목으로(실 도면 파일명이 서술적). 없으면 도면명 라벨 근처."""
    stem = os.path.splitext(os.path.basename(filename or ""))[0].strip()
    if stem:
        return stem[:80]
    lines = [l.strip() for l in (text or "").splitlines() if l.strip()]
    title_label = re.compile(r"(DRAWING\s*TITLE|도면\s*명|TITLE)", re.IGNORECASE)
    for i, line in enumerate(lines):
        if title_label.search(line):
            for j in (i + 1, i + 2):
                if j < len(lines) and lines[j].upper() not in _TITLE_DENY and len(lines[j]) > 2:
                    return lines[j][:80]
    return "Untitled"


def discipline_from_filename(filename: str) -> tuple[str, str]:
    """파일명 선두 번호의 공종 접두로 (code, label) 판정. 미상은 기타."""
    fnum = _filename_number(filename)
    return _discipline(fnum) if fnum else ("G", "G (기타)")


def extract_sheet_meta(text: str, filename: str, page_index: int) -> dict:
    """페이지 텍스트+파일명+페이지인덱스 → {number, title, discipline_code, discipline_label, source}."""
    fnum = _filename_number(filename)
    cands = _candidates(text)

    number = None
    source = "page-index"
    if fnum and fnum in cands:
        number, source = fnum, "filename+page"     # 고신뢰
    elif (lbl := _near_label_number(text)):
        number, source = lbl, "title-block"
    elif fnum:
        number, source = fnum, "filename"
    if not number:
        number = f"Page {page_index + 1}"

    # 공종: 실 번호를 찾았을 때만 번호 접두로 판정. page-index 폴백이면 파일명에서, 그래도 없으면 기타.
    code, label = _discipline(number) if source != "page-index" else _discipline(fnum or "")
    return {
        "number": number,
        "title": _title(text, filename),
        "discipline_code": code,
        "discipline_label": label,
        "meta_source": source,
    }
