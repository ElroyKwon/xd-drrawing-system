const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const BASE = 'http://localhost:3000';
const OUT = path.join(__dirname, 'screenshots');
if (!fs.existsSync(OUT)) fs.mkdirSync(OUT, { recursive: true });

let idx = 0;
const log = [];

async function shot(page, name, desc) {
  idx++;
  const id = String(idx).padStart(2, '0');
  const file = path.join(OUT, `${id}-${name}.png`);
  await page.screenshot({ path: file, fullPage: true });
  console.log(`[${id}] ${desc}`);
  log.push({ id, name, desc, file: `screenshots/${id}-${name}.png` });
  return file;
}

// 분석 실행 버튼이 enabled 될 때까지 기다린 후 클릭
async function runImpact(page) {
  const btn = page.locator('button:has-text("분석 실행")');
  await btn.waitFor({ state: 'visible', timeout: 5000 });
  // enabled 될 때까지 최대 5초 대기
  await page.waitForFunction(() => {
    const b = document.querySelector('button[class*="bg-slate-900"]');
    return b && !b.disabled;
  }, { timeout: 5000 }).catch(() => {});
  await btn.click({ force: true });
  // 분석 완료 대기 (스피너 사라질 때까지)
  await page.waitForTimeout(2000);
}

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1440, height: 900 });

  // ══════════════════════════════════════════════
  // 01. 메인 랜딩
  // ══════════════════════════════════════════════
  await page.goto(BASE, { waitUntil: 'networkidle' });
  await page.waitForTimeout(400);
  await shot(page, 'landing', '메인 랜딩 — 4 페르소나 선택');

  // ══════════════════════════════════════════════
  // P1 기계 — 김기계
  // ══════════════════════════════════════════════
  await page.goto(`${BASE}/p1-mechanical`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(400);
  await shot(page, 'p1-dashboard', 'P1 기계 대시보드 — 즐겨찾기 + 다가오는 정비');

  // 검색창 타이핑 (debounce 확인)
  const searchInput = page.locator('input[placeholder*="설비명"]').first();
  await searchInput.fill('냉동기');
  await page.waitForTimeout(800); // 300ms debounce + 렌더 대기
  await shot(page, 'p1-search', 'P1 검색 — "냉동기" 입력 결과 (debounce 300ms)');
  await searchInput.fill(''); // 검색 초기화

  // CH-001 설비 상세
  await page.goto(`${BASE}/p1-mechanical/entity/CH-001`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(400);
  await shot(page, 'p1-entity-attr', 'P1 CH-001 #1냉동기 — 속성 탭 (verified=true → 뱃지 없음)');

  await page.click('button:has-text("관계")');
  await page.waitForTimeout(300);
  await shot(page, 'p1-entity-rel', 'P1 CH-001 — 관계 탭 (1-hop 상류/하류)');

  await page.click('button:has-text("정비이력")');
  await page.waitForTimeout(300);
  await shot(page, 'p1-entity-maint', 'P1 CH-001 — 정비이력 탭');

  await page.click('button:has-text("위키")');
  await page.waitForTimeout(300);
  await shot(page, 'p1-entity-wiki', 'P1 CH-001 — 위키 탭 (LLM-Wiki)');

  // 신뢰도 툴팁 hover
  const confSpan = page.locator('span.cursor-help').first();
  if (await confSpan.count() > 0) {
    await confSpan.hover();
    await page.waitForTimeout(700);
    await shot(page, 'p1-confidence-tooltip', 'P1 신뢰도 % hover — 툴팁 표시 (ISS-013)');
  }

  // P1 영향도 분석 — URL로 직접 root 지정
  await page.goto(`${BASE}/p1-mechanical/impact?root=CH-001`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(2500); // 자동 분석 완료 대기
  await shot(page, 'p1-impact-result', 'P1 영향도 분석 — 체인 뷰 + CRITICAL 경고 배너 + 하류 3건');

  // 방향 변경 → 양방향
  await page.selectOption('select:has(option[value="both"])', 'both');
  await page.waitForTimeout(200);
  await runImpact(page);
  await shot(page, 'p1-impact-both', 'P1 영향도 — 양방향 분석 결과');

  // 엑셀 버튼 위치
  const excelBtn = page.locator('button:has-text("엑셀")').first();
  if (await excelBtn.count() > 0) {
    await excelBtn.scrollIntoViewIfNeeded();
    await page.waitForTimeout(300);
    await shot(page, 'p1-impact-excel', 'P1 영향도 — 엑셀 내보내기 버튼 (출처·주의 시트 포함)');
  }

  // P1 자연어 질의
  await page.goto(`${BASE}/p1-mechanical/chat`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(400);
  await shot(page, 'p1-chat-sample', 'P1 자연어 질의 — 샘플 질문 화면');

  // 샘플 버튼 클릭
  const s1 = page.locator('button').filter({ hasText: /1차 냉수|냉동기/ }).first();
  await s1.click();
  await page.waitForTimeout(1800);
  await shot(page, 'p1-chat-answer', 'P1 자연어 질의 — 답변 (짧은 텍스트 모드) + "대화 초기화" 버튼');

  // 대화 초기화 버튼 클릭
  const clearBtn = page.locator('button:has-text("대화 초기화")');
  if (await clearBtn.count() > 0) {
    await clearBtn.click();
    await page.waitForTimeout(400);
    await shot(page, 'p1-chat-cleared', 'P1 대화 초기화 후 — 샘플 질문 재표시 (ISS-026)');
  }

  // ══════════════════════════════════════════════
  // P2 전기 — 박전기
  // ══════════════════════════════════════════════
  await page.goto(`${BASE}/p2-electrical`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(500);
  await shot(page, 'p2-dashboard', 'P2 전기 대시보드 — 단선도 + 주요 차단기 목록');

  // VCB-001 설비 상세
  await page.goto(`${BASE}/p2-electrical/entity/VCB-001`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(400);
  await shot(page, 'p2-entity-vcb-attr', 'P2 VCB-001 — 속성 탭 + 미검수(회색) 뱃지 (ISS-001)');

  await page.click('button:has-text("관계")');
  await page.waitForTimeout(300);
  await shot(page, 'p2-entity-vcb-rel', 'P2 VCB-001 — 관계 탭 (하류 4개 VCB)');

  await page.click('button:has-text("위키")');
  await page.waitForTimeout(300);
  await shot(page, 'p2-entity-vcb-wiki', 'P2 VCB-001 — 위키 탭');

  // P2 영향도 — React Flow 그래프
  await page.goto(`${BASE}/p2-electrical/impact?root=VCB-001`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(2500);
  await shot(page, 'p2-impact-graph', 'P2 영향도 — React Flow 그래프 + CRITICAL 배너 (ISS-004)');

  // P2 자연어 질의
  await page.goto(`${BASE}/p2-electrical/chat`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(400);
  const s2 = page.locator('button').filter({ hasText: /VCB-003|TR-001|하류/ }).first();
  await s2.click();
  await page.waitForTimeout(1800);
  await shot(page, 'p2-chat-structured', 'P2 자연어 질의 — 구조화 테이블 답변 (상류/하류 관계)');

  // ══════════════════════════════════════════════
  // P3 소방 — 이소방
  // ══════════════════════════════════════════════
  await page.goto(`${BASE}/p3-fire`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(600);
  await shot(page, 'p3-dashboard', 'P3 소방 대시보드 — SVG 평면도 (Zone-1/Zone-2) + 설비 일람');

  // 평면도 Zone hover
  const poly = page.locator('polygon').first();
  if (await poly.count() > 0) {
    await poly.hover();
    await page.waitForTimeout(500);
    await shot(page, 'p3-zone-hover', 'P3 평면도 Zone-1 마우스 오버 — 강조 표시');
  }

  // FP-001 소방 설비 상세 (정비이력 탭)
  await page.goto(`${BASE}/p3-fire/entity/FP-001`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(400);
  await shot(page, 'p3-entity-fp-attr', 'P3 FP-001 주펌프 — 속성 탭 + 미검수 뱃지');

  await page.click('button:has-text("정비이력")');
  await page.waitForTimeout(300);
  await shot(page, 'p3-entity-fp-maint', 'P3 FP-001 — 정비이력 탭 (ISS-002 적용: 소방도 이력 표시)');

  await page.click('button:has-text("관계")');
  await page.waitForTimeout(300);
  await shot(page, 'p3-entity-fp-rel', 'P3 FP-001 — 관계 탭 (6개 알람밸브에 pressurizes)');

  await page.click('button:has-text("위키")');
  await page.waitForTimeout(300);
  await shot(page, 'p3-entity-fp-wiki', 'P3 FP-001 — 위키 탭 (known_issues 포함)');

  // P3 영향도 — 평면도 오버레이
  await page.goto(`${BASE}/p3-fire/impact?root=FP-001`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(2500);
  await shot(page, 'p3-impact-floor', 'P3 영향도 — 평면도 오버레이 (영향 Zone/마커 색칠)');

  // 마커 hover
  const mk = page.locator('circle').nth(1);
  if (await mk.count() > 0) {
    await mk.hover();
    await page.waitForTimeout(400);
    await shot(page, 'p3-impact-marker', 'P3 평면도 마커 hover — 알람밸브 강조');
  }

  // P3 자연어 질의 (Citation)
  await page.goto(`${BASE}/p3-fire/chat`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(400);
  await shot(page, 'p3-chat-sample', 'P3 소방 자연어 질의 — 샘플 질문');
  const s3 = page.locator('button').filter({ hasText: /점검 주기|Zone|스프링클러/ }).first();
  await s3.click();
  await page.waitForTimeout(1800);
  await shot(page, 'p3-chat-citation', 'P3 소방 자연어 질의 — Citation(원문 인용) 모드 답변');

  // ══════════════════════════════════════════════
  // P4 안전 — 최안전
  // ══════════════════════════════════════════════
  await page.goto(`${BASE}/p4-safety`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(500);
  await shot(page, 'p4-dashboard', 'P4 안전 대시보드 — 분야별 설비 통계 + HITL 검수 대기');

  // HITL 항목 클릭
  await page.goto(`${BASE}/p4-safety/entity/AUX-TR-001`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(400);
  await shot(page, 'p4-entity-hitl', 'P4 AUX-TR-001 — HITL 검수 필요 amber 뱃지 (hitl_flags 존재)');

  // P4 자연어 질의 (Composite)
  await page.goto(`${BASE}/p4-safety/chat`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(400);
  await shot(page, 'p4-chat-sample', 'P4 통합 자연어 질의 — 샘플 질문 (전 분야)');
  const s4 = page.locator('button').filter({ hasText: /이번 달|전 분야|UPS/ }).first();
  await s4.click();
  await page.waitForTimeout(1800);
  await shot(page, 'p4-chat-composite', 'P4 자연어 질의 — Composite 답변 (테이블 + 분석 요약 + 엑셀 버튼)');

  // P4 What-If 시뮬레이션
  await page.goto(`${BASE}/p4-safety/impact`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(500);
  await shot(page, 'p4-whatif-init', 'P4 What-If 초기 — CRITICAL/HIGH 설비 체크박스 목록');

  // 첫 체크박스 클릭
  await page.locator('input[type="checkbox"]').nth(0).check();
  await page.waitForTimeout(300);
  await shot(page, 'p4-whatif-check1', 'P4 What-If — 1번 설비 선택 (빨간 배경 표시)');

  // 두 번째도 선택
  await page.locator('input[type="checkbox"]').nth(1).check();
  await page.waitForTimeout(200);

  // 시뮬레이션 실행
  await page.click('button:has-text("What-If 시뮬레이션")');
  await page.waitForTimeout(1800);
  await shot(page, 'p4-whatif-result', 'P4 What-If 결과 — 분야별 영향 집계 숫자');

  // 공문 초안 스크롤
  const draft = page.locator('pre').first();
  if (await draft.count() > 0) {
    await draft.scrollIntoViewIfNeeded();
    await page.waitForTimeout(400);
    await shot(page, 'p4-whatif-draft', 'P4 공문 초안 — amber 면책 뱃지 + 초안 텍스트 (ISS-003)');
  }

  await browser.close();

  // 캡쳐 인덱스 저장
  fs.writeFileSync(
    path.join(OUT, 'index.json'),
    JSON.stringify(log, null, 2),
    'utf-8'
  );

  console.log(`\n총 ${idx}장 캡쳐 완료`);
  log.forEach(l => console.log(`  [${l.id}] ${l.name}: ${l.desc}`));
})();
