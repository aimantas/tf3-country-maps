// Camera shots of the running game through the bridge. Usage: node take_shots.mjs <id> <windowId> name:x:y:distance ...
// Needs TF3_BRIDGE (path to the companion's bridge.js). Uses macOS screencapture on the game window.
import {execFileSync} from 'node:child_process';
const {request} = await import(process.env.TF3_BRIDGE);
const [id, win, ...specs] = process.argv.slice(2);
const D = new URL(`../shots/${id}`, import.meta.url).pathname; execFileSync('mkdir', ['-p', D]);
for (const s of specs) {
  const [n, x, y, d] = s.split(':');
  await request('camera', {x: +x, y: +y, distance: +d}, 20000);
  await new Promise(r => setTimeout(r, 7000));
  execFileSync('screencapture', ['-l', win, '-o', '-x', `${D}/${n}.png`]);
  console.log('shot', n);
}
