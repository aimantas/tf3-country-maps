// Needs the AI MCP Bridge companion's bridge.js: set TF3_BRIDGE to its path.
const {request} = await import(process.env.TF3_BRIDGE);
import {readFileSync} from 'node:fs';
const id=process.argv[2]; const O=new URL(`../output/${id}`, import.meta.url).pathname;
const want=JSON.parse(readFileSync(`${O}/towns.json`)); const wantInd=JSON.parse(readFileSync(`${O}/industries.json`));
const rows=[];for(let o=0;o<200;o+=20){const e=await request('entities',{kind:'towns',offset:o,limit:20},40000);const it=Array.isArray(e.result.items)?e.result.items:[];rows.push(...it);if(it.length<20)break}
const byName=Object.fromEntries(rows.map(t=>[t.name,t]));
let capOk=0,needOk=0,posOk=0;
for(const w of want){const t=byName[w.name];if(!t)continue;if(t.initialLandUseCapacities.every(c=>c===w.starting_capacities[0]))capOk++;
 const n=JSON.stringify(t.cargoNeeds);if(n.includes('[[9,1]]')&&n.includes('[[13,1]]'))needOk++;
 if(Math.hypot(t.position.x-w.x,t.position.y-w.y)<60)posOk++}
const i=await request('entities',{kind:'industries',offset:0,limit:50},40000);
console.log(JSON.stringify({towns:rows.length,expected:want.length,capacitiesMatch:capOk,needsOnAll:needOk,positionsMatch:posOk,industries:i.result.total,expectedIndustries:wantInd.length}));
