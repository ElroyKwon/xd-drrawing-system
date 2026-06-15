// kb-loader.js — import KB as ES module (file:// 호환, CORS 우회)
import KB from './kb-data.js';
export async function loadKB() {
  return KB;
}
