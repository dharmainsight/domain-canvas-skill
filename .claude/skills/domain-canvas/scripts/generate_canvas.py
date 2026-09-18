#!/usr/bin/env python3
"""Generate a self-contained, accessible Domain Canvas HTML file."""
import argparse
import html
import json
import re
import sys
from pathlib import Path, PurePosixPath

THEME_DEFAULTS = {
    "background": "#f3f4ef",
    "surface": "#ffffff",
    "ink": "#20231c",
    "muted": "#667064",
    "line": "#cfd2c7",
    "accent": "#9b6200",
    "accent_soft": "#fbf3ce",
    "warning": "#9a5a00",
}
HEX_COLOR = re.compile(r"^#[0-9a-fA-F]{3}(?:[0-9a-fA-F]{3})?(?:[0-9a-fA-F]{2})?$")
CARDINALITIES = {"1", "0..1", "1..*", "0..*"}
ROLES = {"primary", "context", "collection", "edit", "create"}
KINDS = {"domain", "database", "both"}
CONFIDENCE = {"confirmed", "inferred"}


def _local_path_ok(value):
    if value in (None, ""):
        return True
    if not isinstance(value, str):
        return False
    low = value.strip().lower()
    if low.startswith(("http://", "https://", "//", "data:", "javascript:")):
        return False
    p = PurePosixPath(value.replace("\\", "/"))
    return not p.is_absolute() and ".." not in p.parts


def validate(model):
    errors = []
    for key in ["title", "version", "entities", "relationships", "screens", "concept_groups"]:
        if key not in model:
            errors.append(f"missing root field: {key}")

    entities = model.get("entities", [])
    screens = model.get("screens", [])
    relationships = model.get("relationships", [])
    groups = model.get("concept_groups", [])

    entity_ids = [e.get("id") for e in entities]
    screen_ids = [s.get("id") for s in screens]
    group_ids = [g.get("id") for g in groups]

    if any(not x for x in entity_ids):
        errors.append("every entity requires a non-empty id")
    if len(entity_ids) != len(set(entity_ids)):
        errors.append("duplicate entity ids")
    if any(not x for x in screen_ids):
        errors.append("every screen requires a non-empty id")
    if len(screen_ids) != len(set(screen_ids)):
        errors.append("duplicate screen ids")
    if len(group_ids) != len(set(group_ids)):
        errors.append("duplicate concept group ids")

    entity_set = set(entity_ids)
    group_set = set(group_ids)
    for e in entities:
        if e.get("group") and e.get("group") not in group_set:
            errors.append(f"entity {e.get('id')} references unknown group={e.get('group')}")
        for a in e.get("attributes", []):
            fk = a.get("fk")
            if fk and fk.get("entity") not in entity_set:
                errors.append(f"entity {e.get('id')} attribute {a.get('name')} has unknown fk entity={fk.get('entity')}")

    for r in relationships:
        rid = r.get("id", "<missing>")
        if r.get("from") not in entity_set:
            errors.append(f"relationship {rid} has unknown from={r.get('from')}")
        if r.get("to") not in entity_set:
            errors.append(f"relationship {rid} has unknown to={r.get('to')}")
        if r.get("kind") not in KINDS:
            errors.append(f"relationship {rid} has invalid kind={r.get('kind')}")
        if r.get("confidence") not in CONFIDENCE:
            errors.append(f"relationship {rid} has invalid confidence={r.get('confidence')}")
        for key in ("from_cardinality", "to_cardinality"):
            if r.get(key) not in CARDINALITIES:
                errors.append(f"relationship {rid} has invalid {key}={r.get(key)}")

    for s in screens:
        sid = s.get("id", "<missing>")
        primary = 0
        for b in s.get("bindings", []):
            if b.get("entity") not in entity_set:
                errors.append(f"screen {sid} binds unknown entity={b.get('entity')}")
            if b.get("role") not in ROLES:
                errors.append(f"screen {sid} has invalid binding role={b.get('role')}")
            if b.get("role") == "primary":
                primary += 1
        if primary > 1:
            errors.append(f"screen {sid} has {primary} primary bindings; confirm this is intentional before generation")
        for key in ("preview_image", "preview_html"):
            if not _local_path_ok(s.get(key)):
                errors.append(f"screen {sid} {key} must be a local relative path")

    presentation = model.get("presentation") or {}
    focus = presentation.get("focus_entities") or []
    if len(focus) > 2:
        errors.append("presentation.focus_entities may contain at most two entities")
    for fid in focus:
        if fid not in entity_set:
            errors.append(f"presentation.focus_entities contains unknown entity={fid}")
    theme = presentation.get("theme") or {}
    for key, value in theme.items():
        if key not in THEME_DEFAULTS:
            errors.append(f"unsupported presentation.theme key={key}")
        elif not isinstance(value, str) or not HEX_COLOR.match(value):
            errors.append(f"presentation.theme.{key} must be a hex color")

    return errors


def theme_for(model):
    theme = dict(THEME_DEFAULTS)
    theme.update((model.get("presentation") or {}).get("theme") or {})
    return theme


TEMPLATE = r'''<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>__TITLE__</title>
<style>
:root{
  --bg:__BACKGROUND__;--panel:__SURFACE__;--ink:__INK__;--muted:__MUTED__;--line:__LINE__;
  --accent:__ACCENT__;--accent-soft:__ACCENT_SOFT__;--warn:__WARNING__;--stage-w:2200px;--stage-h:1400px
}
*{box-sizing:border-box}html,body{width:100%;height:100%;margin:0;font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color:var(--ink);background:var(--bg);overflow:hidden}
button{font:inherit}.app{width:100%;height:100%;display:flex;flex-direction:column}.top{min-height:60px;background:var(--panel);border-bottom:1px solid var(--line);display:flex;align-items:center;padding:9px 16px;gap:14px;z-index:10}.brand{font-weight:760;white-space:nowrap;max-width:34vw;overflow:hidden;text-overflow:ellipsis}.views{display:flex;gap:2px;border:1px solid var(--line);border-radius:7px;padding:3px;background:var(--bg)}.views button{border:0;background:transparent;padding:7px 11px;border-radius:4px;color:var(--muted);font-weight:680;cursor:pointer}.views button[aria-selected="true"]{background:var(--panel);color:var(--ink);box-shadow:0 0 0 1px var(--line)}.meta{margin-left:auto;font-size:12px;color:var(--muted)}
#viewport{position:relative;flex:1;overflow:hidden;cursor:grab;background:var(--bg);outline:none}#viewport.dragging{cursor:grabbing}#viewport:focus-visible{outline:3px solid var(--accent);outline-offset:-3px}#stage{position:absolute;left:0;top:0;width:var(--stage-w);height:var(--stage-h);transform-origin:0 0}#edges{position:absolute;inset:0;width:var(--stage-w);height:var(--stage-h);overflow:visible;pointer-events:none}.layer{position:absolute;inset:0}
.node{position:absolute;background:var(--panel);border:1px solid var(--line);border-radius:7px;overflow:hidden;box-shadow:0 1px 0 #00000008}.node:focus-visible{outline:3px solid var(--accent);outline-offset:3px}.node.focus{border-color:var(--accent);box-shadow:inset 4px 0 0 var(--accent)}.node .hd{padding:10px 12px;border-bottom:1px solid var(--line);display:flex;align-items:center;gap:8px;font-weight:760}.node .body{padding:11px 12px;font-size:12px;color:var(--muted);line-height:1.5}.entity{width:300px}.entity .desc{min-height:36px}.pill{font-size:10px;font-weight:760;padding:2px 6px;border-radius:999px;background:var(--bg);color:var(--muted);margin-left:auto;border:1px solid var(--line)}.focus .pill{background:var(--accent-soft);color:var(--ink);border-color:transparent}.attr{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:8px;padding:5px 0;border-bottom:1px dashed var(--line);color:var(--ink)}.attr:last-child{border-bottom:0}.key{font-size:10px;padding:2px 5px;border:1px solid var(--line);border-radius:4px;color:var(--muted)}
.screen{width:430px;min-height:250px}.screen .preview{height:160px;background:var(--bg);border-bottom:1px solid var(--line);display:flex;align-items:center;justify-content:center;overflow:hidden}.screen img,.screen iframe{width:100%;height:100%;object-fit:cover;border:0;background:var(--panel)}.mock{width:88%;height:76%;background:var(--panel);border:1px solid var(--line);display:flex}.mock aside{width:25%;border-right:1px solid var(--line);padding:10px}.mock main{flex:1;padding:10px}.sk{height:7px;background:var(--line);margin:7px 0}.sk.s{width:55%}.sk.m{width:75%}.bindings{display:flex;gap:5px;flex-wrap:wrap;margin-top:8px}.binding{font-size:10px;padding:4px 6px;border:1px solid var(--line);border-radius:4px;color:var(--muted);background:var(--panel)}.binding.direct{border-color:var(--accent);color:var(--ink)}
.lane{position:absolute;border:1px solid var(--line);background:#ffffff54;border-radius:8px;padding:46px 16px 16px}.lane .lane-title{position:absolute;top:13px;left:16px;right:16px;font-size:11px;font-weight:800;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);display:flex;justify-content:space-between;gap:12px}.lane .lane-desc{font-weight:500;letter-spacing:0;text-transform:none;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.summary{width:320px}.summary .metric{font-size:25px;font-weight:800;color:var(--ink);line-height:1}.summary ul{padding-left:17px;margin:10px 0 0}.summary li{margin:3px 0}.edge-label{font-size:11px;fill:var(--muted);paint-order:stroke;stroke:var(--bg);stroke-width:6px;stroke-linejoin:round}.edge-label.inferred{font-style:italic}.legend{position:absolute;right:14px;top:74px;z-index:7;background:var(--panel);border:1px solid var(--line);border-radius:7px;padding:9px 11px;font-size:11px;color:var(--muted);max-width:230px}.legend .line{display:inline-block;width:22px;border-top:2px solid var(--accent);vertical-align:middle;margin-right:6px}.legend .line.dashed{border-top-style:dashed;border-top-color:var(--warn);margin-left:10px}.toolbar{position:absolute;left:50%;bottom:16px;transform:translateX(-50%);z-index:9;background:var(--panel);border:1px solid var(--line);border-radius:7px;padding:5px;display:flex;gap:2px}.toolbar button{border:0;background:transparent;border-radius:4px;padding:7px 9px;cursor:pointer;color:var(--muted)}.toolbar button:hover,.toolbar button:focus-visible{background:var(--bg);color:var(--ink);outline:none}.toolbar button[aria-pressed="true"]{background:var(--accent-soft);color:var(--ink)}.sr-only{position:absolute!important;width:1px!important;height:1px!important;padding:0!important;margin:-1px!important;overflow:hidden!important;clip:rect(0,0,0,0)!important;white-space:nowrap!important;border:0!important}
@media(max-width:720px){.top{flex-wrap:wrap}.brand{max-width:100%;width:100%}.meta{display:none}.legend{top:auto;bottom:62px;right:8px;max-width:190px}.toolbar{bottom:10px}.views button{padding:7px 9px}}
@media(prefers-reduced-motion:reduce){*{scroll-behavior:auto!important;animation:none!important;transition:none!important}}
@media print{html,body{overflow:visible;height:auto}.top,.toolbar,.legend{display:none!important}#viewport{overflow:visible;height:auto;min-height:100vh}#stage{transform:none!important;position:relative}.node,.lane{break-inside:avoid}}
</style>
</head>
<body>
<div class="app">
  <header class="top">
    <div class="brand">__TITLE__</div>
    <div class="views" role="tablist" aria-label="Domain Canvas views">
      <button id="tab-design" role="tab" aria-selected="true" aria-controls="viewport" data-view="design">Design</button>
      <button id="tab-concept" role="tab" aria-selected="false" aria-controls="viewport" data-view="concept">Concept</button>
      <button id="tab-er" role="tab" aria-selected="false" aria-controls="viewport" data-view="er">ER</button>
    </div>
    <div class="meta">single source · model.json</div>
  </header>
  <div id="viewport" tabindex="0" aria-label="Interactive domain canvas. Drag to pan and use the controls to zoom.">
    <div id="stage">
      <svg id="edges" role="img" aria-labelledby="edge-title edge-desc"><title id="edge-title">Domain relationships</title><desc id="edge-desc">Confirmed relationships use solid lines. Inferred relationships use dashed lines and are labeled inferred.</desc></svg>
      <div id="lanes" class="layer" aria-hidden="true"></div>
      <div id="nodes" class="layer"></div>
    </div>
  </div>
  <div class="legend" aria-label="Relationship legend"><span class="line"></span>confirmed <span class="line dashed"></span>inferred</div>
  <div class="toolbar" aria-label="Canvas controls">
    <button id="detail" type="button" hidden aria-pressed="false">Detail</button>
    <button id="fit" type="button">Fit</button><button id="zin" type="button" aria-label="Zoom in">＋</button><button id="zout" type="button" aria-label="Zoom out">－</button><button id="reset" type="button">100%</button>
  </div>
  <p id="status" class="sr-only" aria-live="polite"></p>
</div>
<script id="model" type="application/json">__PAYLOAD__</script>
<script>
const data=JSON.parse(document.getElementById('model').textContent);
const viewport=document.getElementById('viewport'),stage=document.getElementById('stage'),nodes=document.getElementById('nodes'),lanes=document.getElementById('lanes'),svg=document.getElementById('edges'),status=document.getElementById('status');
const focus=new Set((data.presentation&&data.presentation.focus_entities)||[]);
const entityById=Object.fromEntries(data.entities.map(e=>[e.id,e]));
const groupById=Object.fromEntries((data.concept_groups||[]).map(g=>[g.id,g]));
const DIRECT_ROLES=new Set(['primary','edit','create']);
let view='design',detail=data.entities.length<=9,tx=70,ty=50,scale=.82,drag=null;
const detailButton=document.getElementById('detail');
if(data.entities.length>9) detailButton.hidden=false;
function esc(s){return String(s??'').replace(/[&<>\"]/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[m]))}
function setStageSize(w,h){document.documentElement.style.setProperty('--stage-w',Math.max(1500,w)+'px');document.documentElement.style.setProperty('--stage-h',Math.max(1000,h)+'px')}
function applyTransform(){stage.style.transform=`translate(${tx}px,${ty}px) scale(${scale})`}
function clear(){nodes.innerHTML='';lanes.innerHTML='';svg.querySelectorAll('path,text').forEach(x=>x.remove())}
function addNode(id,cls,x,y,body,label){const d=document.createElement('div');d.className='node '+cls+(focus.has(id)?' focus':'');d.id='n-'+id;d.style.left=x+'px';d.style.top=y+'px';d.innerHTML=body;d.tabIndex=0;d.setAttribute('role','group');d.setAttribute('aria-label',label||id);nodes.appendChild(d);return d}
function addLane(id,x,y,w,h,title,desc=''){const d=document.createElement('div');d.className='lane';d.id='lane-'+id;d.style.left=x+'px';d.style.top=y+'px';d.style.width=w+'px';d.style.height=h+'px';d.innerHTML=`<div class="lane-title"><span>${esc(title)}</span><span class="lane-desc">${esc(desc)}</span></div>`;lanes.appendChild(d);return d}
function mock(){return `<div class="mock"><aside><div class="sk m"></div><div class="sk"></div><div class="sk s"></div><div class="sk"></div></aside><main><div class="sk s"></div><div class="sk"></div><div class="sk"></div><div class="sk m"></div><div class="sk"></div><div class="sk s"></div></main></div>`}
function screenHTML(s){let p=mock();if(s.preview_html)p=`<iframe src="${esc(s.preview_html)}" loading="lazy" title="${esc(s.name)} preview"></iframe>`;else if(s.preview_image)p=`<img src="${esc(s.preview_image)}" alt="${esc(s.name)} preview"/>`;const bs=(s.bindings||[]).map(b=>`<span class="binding ${DIRECT_ROLES.has(b.role)?'direct':''}">${esc(entityById[b.entity]?.name||b.entity)} · ${esc(b.role)}</span>`).join('');return `<div class="hd">${esc(s.name)}<span class="pill">${esc(s.route||'screen')}</span></div><div class="preview">${p}</div><div class="body">${esc(s.description||'')}<div class="bindings">${bs}</div></div>`}
function conceptHTML(e){return `<div class="hd">${esc(e.name)}<span class="pill">${esc(e.group||'entity')}</span></div><div class="body"><div class="desc">${esc(e.description||'')}</div></div>`}
function erHTML(e,compact=false){const attrs=(e.attributes||[]).filter(a=>!compact||a.pk||a.fk).map(a=>{let k=[];if(a.pk)k.push('PK');if(a.fk)k.push('FK');return `<div class="attr"><span>${esc(a.name)} <span style="color:var(--muted)">${esc(a.type||'')}</span></span>${k.length?`<span class="key">${k.join(' · ')}</span>`:''}</div>`}).join('');return `<div class="hd">${esc(e.name)}<span class="pill">${compact?'keys':'table'}</span></div><div class="body">${attrs||'<span>No attributes</span>'}</div>`}
function summaryHTML(title,count,label,names){return `<div class="hd">${esc(title)}<span class="pill">overview</span></div><div class="body"><div class="metric">${count}</div><div>${esc(label)}</div><ul>${names.slice(0,6).map(n=>`<li>${esc(n)}</li>`).join('')}${names.length>6?`<li>+${names.length-6} more</li>`:''}</ul></div>`}
function center(el){return [el.offsetLeft+el.offsetWidth/2,el.offsetTop+el.offsetHeight/2]}
function edge(a,b,label,inferred=false,card=''){const A=document.getElementById('n-'+a),B=document.getElementById('n-'+b);if(!A||!B)return;const [x1,y1]=center(A),[x2,y2]=center(B);const dx=x2-x1,dy=y2-y1;let sx=x1,sy=y1,ex=x2,ey=y2;if(Math.abs(dx)>Math.abs(dy)){sx+=Math.sign(dx)*A.offsetWidth/2;ex-=Math.sign(dx)*B.offsetWidth/2}else{sy+=Math.sign(dy)*A.offsetHeight/2;ey-=Math.sign(dy)*B.offsetHeight/2}const ns='http://www.w3.org/2000/svg',path=document.createElementNS(ns,'path');const mx=(sx+ex)/2;path.setAttribute('d',`M ${sx} ${sy} C ${mx} ${sy}, ${mx} ${ey}, ${ex} ${ey}`);path.setAttribute('fill','none');path.setAttribute('stroke',inferred?'var(--warn)':'var(--accent)');path.setAttribute('stroke-width','1.8');if(inferred)path.setAttribute('stroke-dasharray','7 6');svg.appendChild(path);if(label||card){const t=document.createElementNS(ns,'text');t.setAttribute('x',mx);t.setAttribute('y',(sy+ey)/2-6);t.setAttribute('text-anchor','middle');t.setAttribute('class','edge-label'+(inferred?' inferred':''));t.textContent=(label||'')+(card?` · ${card}`:'')+(inferred?' · inferred':'');svg.appendChild(t)}}
function groupsWithEntities(){const map=new Map();(data.concept_groups||[]).forEach(g=>map.set(g.id,{group:g,entities:[]}));map.set('__other__',{group:{id:'__other__',name:'Other',description:''},entities:[]});data.entities.forEach(e=>{const k=(e.group&&map.has(e.group))?e.group:'__other__';map.get(k).entities.push(e)});return [...map.values()].filter(x=>x.entities.length)}
function placeLanes(mode){const groups=groupsWithEntities(),cols=3,colW=390,baseX=100,gapY=34,heights=[100,100,100],positions={};groups.forEach(item=>{let col=heights.indexOf(Math.min(...heights));const x=baseX+col*colW,y=heights[col];let innerY=y+58;let laneH=72;item.entities.forEach(e=>{const attrCount=(e.attributes||[]).length;const h=mode==='er'?Math.max(145,92+attrCount*30):130;positions[e.id]={x:x+24,y:innerY};innerY+=h+20;laneH+=h+20});laneH=Math.max(190,laneH);addLane(item.group.id,x,y,350,laneH,item.group.name,item.group.description||'');heights[col]=y+laneH+gapY});setStageSize(baseX+cols*colW+140,Math.max(...heights)+100);return positions}
function renderDesign(){const screens=data.screens||[],directIds=[];screens.forEach(s=>(s.bindings||[]).forEach(b=>{if(DIRECT_ROLES.has(b.role)&&!directIds.includes(b.entity))directIds.push(b.entity)}));screens.forEach((s,i)=>{const col=i%2,row=Math.floor(i/2);addNode('screen-'+s.id,'screen',120+col*520,110+row*360,screenHTML(s),`Screen ${s.name}`)});directIds.forEach((id,i)=>{const e=entityById[id];if(e)addNode(id,'entity',1250+(i%2)*350,110+Math.floor(i/2)*180,conceptHTML(e),`Entity ${e.name}`)});setStageSize(2050,Math.max(1000,220+Math.ceil(Math.max(screens.length,1)/2)*360,220+Math.ceil(Math.max(directIds.length,1)/2)*180));requestAnimationFrame(()=>screens.forEach(s=>(s.bindings||[]).filter(b=>DIRECT_ROLES.has(b.role)).forEach(b=>edge('screen-'+s.id,b.entity,b.role,false,''))))}
function renderConceptDetail(){const pos=placeLanes('concept');data.entities.forEach(e=>addNode(e.id,'entity',pos[e.id].x,pos[e.id].y,conceptHTML(e),`Concept ${e.name}`));requestAnimationFrame(()=>data.relationships.forEach(r=>edge(r.from,r.to,r.label,r.confidence==='inferred',`${r.from_cardinality} → ${r.to_cardinality}`)))}
function groupKey(entityId){return entityById[entityId]?.group||'__other__'}
function renderOverview(kind){const gs=groupsWithEntities();gs.forEach((item,i)=>{const col=i%3,row=Math.floor(i/3),x=120+col*390,y=120+row*300;let keyCount=item.entities.reduce((n,e)=>n+(e.attributes||[]).filter(a=>a.pk||a.fk).length,0);const label=kind==='er'?`${keyCount} PK/FK fields`:'entities';addNode('group-'+item.group.id,'summary',x,y,summaryHTML(item.group.name,item.entities.length,label,item.entities.map(e=>e.name)),`${item.group.name} overview`)});setStageSize(1450,Math.max(900,250+Math.ceil(gs.length/3)*300));const aggregates=new Map();data.relationships.filter(r=>kind!=='er'||r.kind!=='domain').forEach(r=>{const a=groupKey(r.from),b=groupKey(r.to);if(a===b)return;const key=[a,b].sort().join('|');aggregates.set(key,(aggregates.get(key)||0)+1)});requestAnimationFrame(()=>aggregates.forEach((count,key)=>{const [a,b]=key.split('|');edge('group-'+a,'group-'+b,`${count} relation${count===1?'':'s'}`,false,'')}))}
function renderERDetail(){const pos=placeLanes('er');data.entities.forEach(e=>addNode(e.id,'entity',pos[e.id].x,pos[e.id].y,erHTML(e,false),`ER entity ${e.name}`));requestAnimationFrame(()=>data.relationships.filter(r=>r.kind!=='domain').forEach(r=>edge(r.from,r.to,r.label,r.confidence==='inferred',`${r.from_cardinality} → ${r.to_cardinality}`)))}
function updateDetailButton(){if(data.entities.length<=9)return;detailButton.textContent=detail?'Overview':'Detail';detailButton.setAttribute('aria-pressed',detail?'true':'false')}
function render(){clear();if(view==='design')renderDesign();else if(view==='concept'){if(data.entities.length>9&&!detail)renderOverview('concept');else renderConceptDetail()}else{if(data.entities.length>9&&!detail)renderOverview('er');else renderERDetail()}updateDetailButton();setTimeout(fit,40);status.textContent=`${view} view, ${data.entities.length>9?(detail?'detail':'overview'):'detail'} mode`}
function fit(){const els=[...document.querySelectorAll('.node,.lane')];if(!els.length)return;let minx=Infinity,miny=Infinity,maxx=-Infinity,maxy=-Infinity;els.forEach(e=>{minx=Math.min(minx,e.offsetLeft);miny=Math.min(miny,e.offsetTop);maxx=Math.max(maxx,e.offsetLeft+e.offsetWidth);maxy=Math.max(maxy,e.offsetTop+e.offsetHeight)});const w=maxx-minx,h=maxy-miny,vw=viewport.clientWidth,vh=viewport.clientHeight;scale=Math.min(.96,(vw-100)/w,(vh-90)/h);scale=Math.max(.26,scale);tx=(vw-w*scale)/2-minx*scale;ty=(vh-h*scale)/2-miny*scale;applyTransform()}
[...document.querySelectorAll('.views button')].forEach(b=>b.addEventListener('click',()=>{view=b.dataset.view;document.querySelectorAll('.views button').forEach(x=>x.setAttribute('aria-selected',x===b?'true':'false'));render()}));
detailButton.addEventListener('click',()=>{detail=!detail;render()});
viewport.addEventListener('wheel',e=>{e.preventDefault();const rect=viewport.getBoundingClientRect(),mx=e.clientX-rect.left,my=e.clientY-rect.top,old=scale;scale=Math.max(.2,Math.min(2.2,scale*(e.deltaY<0?1.1:.9)));tx=mx-(mx-tx)*(scale/old);ty=my-(my-ty)*(scale/old);applyTransform()},{passive:false});
viewport.addEventListener('pointerdown',e=>{if(e.button!==0)return;drag={x:e.clientX,y:e.clientY,tx,ty};viewport.setPointerCapture(e.pointerId);viewport.classList.add('dragging')});
viewport.addEventListener('pointermove',e=>{if(!drag)return;tx=drag.tx+(e.clientX-drag.x);ty=drag.ty+(e.clientY-drag.y);applyTransform()});
viewport.addEventListener('pointerup',()=>{drag=null;viewport.classList.remove('dragging')});
viewport.addEventListener('keydown',e=>{const step=e.shiftKey?80:30;if(e.key==='ArrowLeft')tx+=step;else if(e.key==='ArrowRight')tx-=step;else if(e.key==='ArrowUp')ty+=step;else if(e.key==='ArrowDown')ty-=step;else return;e.preventDefault();applyTransform()});
document.getElementById('fit').onclick=fit;document.getElementById('zin').onclick=()=>{scale=Math.min(2.2,scale*1.15);applyTransform()};document.getElementById('zout').onclick=()=>{scale=Math.max(.2,scale/1.15);applyTransform()};document.getElementById('reset').onclick=()=>{scale=1;tx=40;ty=40;applyTransform()};window.addEventListener('resize',fit);render();
</script>
</body></html>'''


def main():
    parser = argparse.ArgumentParser(description="Generate interactive Domain Canvas HTML")
    parser.add_argument("--model", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    model_path = Path(args.model)
    out_path = Path(args.out)
    model = json.loads(model_path.read_text(encoding="utf-8"))
    errors = validate(model)
    if errors:
        print("Model validation failed:", file=sys.stderr)
        for error in errors:
            print(" - " + error, file=sys.stderr)
        raise SystemExit(2)

    payload = json.dumps(model, ensure_ascii=False).replace("</", "<\\/")
    title = html.escape(str(model.get("title", "Domain Canvas")))
    theme = theme_for(model)
    replacements = {
        "__TITLE__": title,
        "__PAYLOAD__": payload,
        "__BACKGROUND__": theme["background"],
        "__SURFACE__": theme["surface"],
        "__INK__": theme["ink"],
        "__MUTED__": theme["muted"],
        "__LINE__": theme["line"],
        "__ACCENT__": theme["accent"],
        "__ACCENT_SOFT__": theme["accent_soft"],
        "__WARNING__": theme["warning"],
    }
    document = TEMPLATE
    for key, value in replacements.items():
        document = document.replace(key, value)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(document, encoding="utf-8")
    mode = "overview-first" if len(model["entities"]) > 9 else "detail"
    print(
        f"Generated {out_path} ({len(model['entities'])} entities, {len(model['screens'])} screens, "
        f"{len(model['relationships'])} relationships, {mode})"
    )


if __name__ == "__main__":
    main()
