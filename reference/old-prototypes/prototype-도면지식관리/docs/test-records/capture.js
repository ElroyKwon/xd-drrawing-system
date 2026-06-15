const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const BASE = 'http://localhost:3000';
const OUT = path.join(__dirname, 'screenshots');
if (!fs.existsSync(OUT)) fs.mkdirSync(OUT, { recursive: true });

const SCREENS = [
  // 메인
  { id: '01-landing',      url: '/',                           desc: '메인 랜딩 — 4 페르소나 선택', wait: 500 },
  // P1 기계
  { id: '02-p1-dashboard', url: '/p1-mechanical',             desc: 'P1 기계 대시보드 (즐겨찾기 + 다가오는 정비)', wait: 500 },
  { id: '03-p1-entity',    url: '/p1-mechanical/entity/CH-001', desc: 'P1 설비 상세 — CH-001 냉동기 (verified=true, 뱃지없음)', wait: 500 },
  { id: '04-p1-entity-vcb',url: '/p2-electrical/entity/VCB-001', desc: 'P2 설비 상세 — VCB-001 (미검수 뱃지)', wait: 500 },
  { id: '05-p1-chat',      url: '/p1-mechanical/chat',        desc: 'P1 자연어 질의 (샘플 쿼리 화면)', wait: 500 },
  { id: '06-p1-impact',    url: '/p1-mechanical/impact',      desc: 'P1 영향도 분석 (체인 뷰)', wait: 500 },
  // P2 전기
  { id: '07-p2-dashboard', url: '/p2-electrical',             desc: 'P2 전기 대시보드 (단선도 + 회로 목록)', wait: 500 },
  { id: '08-p2-impact',    url: '/p2-electrical/impact',      desc: 'P2 영향도 분석 (React Flow 그래프)', wait: 500 },
  // P3 소방
  { id: '09-p3-dashboard', url: '/p3-fire',                   desc: 'P3 소방 대시보드 (SVG 평면도 인터랙티브)', wait: 600 },
  { id: '10-p3-entity-fp', url: '/p3-fire/entity/FP-001',    desc: 'P3 소방 FP-001 — 정비이력 탭 표시 (ISS-002)', wait: 500 },
  { id: '11-p3-impact',    url: '/p3-fire/impact',            desc: 'P3 영향도 분석 (SVG 평면도 오버레이)', wait: 500 },
  // P4 안전
  { id: '12-p4-dashboard', url: '/p4-safety',                 desc: 'P4 안전 대시보드 (분야별 통계 + HITL)', wait: 500 },
  { id: '13-p4-impact',    url: '/p4-safety/impact',          desc: 'P4 What-If 시뮬레이션', wait: 600 },
  // 특정 이슈 확인
  { id: '14-p1-impact-run',url: '/p1-mechanical/impact?root=CH-001', desc: 'P1 영향도 분석 실행 — CH-001 결과 (체인)', wait: 2000 },
  { id: '15-p2-impact-run',url: '/p2-electrical/impact?root=VCB-001', desc: 'P2 영향도 분석 — VCB-001 (그래프+CRITICAL 배너)', wait: 2000 },
];

(async () => {
  console.log('브라우저 시작...');
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1440, height: 900 });

  const results = [];

  for (const s of SCREENS) {
    const url = BASE + s.url;
    console.log(`캡쳐: ${s.id} — ${url}`);
    try {
      await page.goto(url, { waitUntil: 'networkidle', timeout: 10000 });
      await page.waitForTimeout(s.wait);
      const file = path.join(OUT, `${s.id}.png`);
      await page.screenshot({ path: file, fullPage: true });
      console.log(`  → ${file}`);
      results.push({ id: s.id, desc: s.desc, file: `screenshots/${s.id}.png`, ok: true });
    } catch (e) {
      console.error(`  ERROR: ${e.message}`);
      results.push({ id: s.id, desc: s.desc, file: '', ok: false, err: e.message });
    }
  }

  // 추가: What-If 실행 캡쳐 (버튼 클릭)
  console.log('What-If 시뮬레이션 실행 캡쳐...');
  try {
    await page.goto(BASE + '/p4-safety/impact', { waitUntil: 'networkidle', timeout: 10000 });
    await page.waitForTimeout(500);
    // CRITICAL/HIGH 첫 번째 체크박스 클릭
    const checkboxes = await page.locator('input[type="checkbox"]').all();
    if (checkboxes.length > 0) {
      await checkboxes[0].check();
      await page.waitForTimeout(300);
    }
    const btn = page.locator('button:has-text("What-If 시뮬레이션")');
    if (await btn.count() > 0) {
      await btn.click();
      await page.waitForTimeout(1500);
    }
    const file = path.join(OUT, '16-p4-whatif-result.png');
    await page.screenshot({ path: file, fullPage: true });
    results.push({ id: '16-p4-whatif-result', desc: 'P4 What-If 결과 — 공문 초안 + 면책 경고', file: 'screenshots/16-p4-whatif-result.png', ok: true });
    console.log(`  → ${file}`);
  } catch (e) {
    console.error(`  What-If 실행 ERROR: ${e.message}`);
  }

  // 추가: Chat 질문 입력 후 캡쳐
  console.log('Chat 질문 입력 캡쳐...');
  try {
    await page.goto(BASE + '/p1-mechanical/chat', { waitUntil: 'networkidle', timeout: 10000 });
    await page.waitForTimeout(500);
    const sampleBtns = await page.locator('button:has-text("냉동기")').all();
    if (sampleBtns.length > 0) {
      await sampleBtns[0].click();
      await page.waitForTimeout(2000);
    } else {
      const input = page.locator('input[placeholder*="질문"]');
      await input.fill('CH-001 정비 이력');
      await page.locator('button[type="submit"]').click();
      await page.waitForTimeout(2000);
    }
    const file = path.join(OUT, '17-p1-chat-answer.png');
    await page.screenshot({ path: file, fullPage: true });
    results.push({ id: '17-p1-chat-answer', desc: 'P1 Chat 답변 화면 (대화 초기화 버튼 포함)', file: 'screenshots/17-p1-chat-answer.png', ok: true });
    console.log(`  → ${file}`);
  } catch (e) {
    console.error(`  Chat ERROR: ${e.message}`);
  }

  await browser.close();

  // 결과 JSON 저장
  fs.writeFileSync(path.join(OUT, 'index.json'), JSON.stringify(results, null, 2), 'utf-8');
  const ok = results.filter(r => r.ok).length;
  console.log(`\n완료: ${ok}/${results.length} 캡쳐 성공`);
  results.filter(r => !r.ok).forEach(r => console.log(`  FAIL: ${r.id} — ${r.err}`));
})();
