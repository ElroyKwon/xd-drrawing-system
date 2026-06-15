/**
 * knowledge-base YAML 로더.
 * - js-yaml 을 CDN ESM 으로 동적 import.
 * - sheets/arch_p062.yml + level-stack.yml 을 fetch & 파싱.
 */

export async function loadKB({ sheetId = 'arch_p062' } = {}) {
  // js-yaml ESM CDN
  const { default: jsyaml } = await import('https://cdn.jsdelivr.net/npm/js-yaml@4.1.0/+esm');

  const sheetUrl = `../../knowledge-base/sheets/${sheetId}.yml`;
  const levelsUrl = `../../knowledge-base/level-stack.yml`;

  const [sheetText, levelsText] = await Promise.all([
    fetch(sheetUrl).then(r => {
      if (!r.ok) throw new Error(`sheet YAML ${sheetUrl}: ${r.status}`);
      return r.text();
    }),
    fetch(levelsUrl).then(r => {
      if (!r.ok) throw new Error(`levels YAML ${levelsUrl}: ${r.status}`);
      return r.text();
    }),
  ]);

  const sheet = jsyaml.load(sheetText);
  const levelStack = jsyaml.load(levelsText);
  return { sheet, levelStack };
}
