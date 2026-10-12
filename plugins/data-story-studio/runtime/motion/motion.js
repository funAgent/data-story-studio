(function(root){
const clamp=(x)=>Math.max(0,Math.min(1,x));
const ease=x=>1-Math.pow(1-clamp(x),3);
function validate(p){
 const fail=m=>{throw Error(m)};
 const str=(v,n)=>typeof v==='string'&&v.length<=n&&!/[\u0000-\u001f]/.test(v);
 if(!p||p.schemaVersion!==1)fail('Unsupported schemaVersion');
 if(p.width!==1280||p.height!==720)fail('Only 1280x720 supported');
 if(!Number.isInteger(p.fps)||p.fps<1||p.fps>60)fail('fps must be 1..60');
 if(!Number.isInteger(p.durationFrames)||p.durationFrames<30||p.durationFrames>1800)fail('durationFrames must be 30..1800');
 if(!str(p.title,140))fail('Title must be a string <=140 characters with no control characters');
 if(!p.theme||!['background','foreground','accent','muted'].every(k=>/^#[0-9a-f]{6}$/i.test(p.theme[k])))fail('Invalid theme');
 if(!p.source||JSON.stringify(p.source.columns)!=='["category","value"]'||!Array.isArray(p.source.rows)||p.source.rows.length<2||p.source.rows.length>8)fail('Expected 2..8 category/value rows');
 if(!str(p.source.label,140)||!str(p.source.valuePrefix,12)||!str(p.source.valueSuffix,12))fail('Invalid source labels');
 const cats=new Set();for(const r of p.source.rows){if(!Array.isArray(r)||r.length!==2||!str(r[0],20)||!r[0]||cats.has(r[0])||!Number.isFinite(r[1])||r[1]<0||r[1]>1e12)fail('Invalid or duplicate category/value');cats.add(r[0]);}
 if(!Array.isArray(p.scenes)||p.scenes.length<1||p.scenes.length>12)fail('Expected 1..12 scenes');
 let end=0;const ids=new Set();for(const s of p.scenes){
 if(!s||!str(s.id,64)||!s.id||ids.has(s.id))fail('Invalid or duplicate scene id');ids.add(s.id);
 if(!['headline','barChart','summary'].includes(s.type))fail('Only headline, barChart, summary supported');
 if(!Number.isInteger(s.start)||s.start!==end||!Number.isInteger(s.duration)||s.duration<30||s.duration>1800)fail('Scenes must be contiguous, each 30..1800 frames');end+=s.duration;
 for(const k of ['title','subtitle'])if(!str(s[k],140))fail('Invalid '+k);
 for(const k of ['metric','metricLabel'])if((s.type!=='barChart'||s[k]!==undefined)&&!str(s[k],140))fail('Invalid '+k);
 }if(end!==p.durationFrames)fail('Scene duration mismatch');return p;
}
function render(canvas,p,frame){
 const c=canvas.getContext('2d');canvas.width=p.width;canvas.height=p.height;const t=p.theme;
 c.fillStyle=t.background;c.fillRect(0,0,1280,720);
 const text=(str,x,y,size,color=t.foreground,weight=400,maxWidth=1200-x)=>{const font=n=>`${weight} ${n}px \"Liberation Sans\", \"Arial\", \"Noto Sans CJK SC\", \"Noto Sans CJK JP\", sans-serif`;c.font=font(size);const w=c.measureText(str).width;if(w>maxWidth)c.font=font(Math.max(12,size*maxWidth/w));c.fillStyle=color;c.fillText(str,x,y,maxWidth)};
 text('MOTION / DATA STORIES',72,58,16,t.muted,600);text('DATA STORY',1090,58,15,t.muted);
 const s=p.scenes.find(s=>frame>=s.start&&frame<s.start+s.duration)||p.scenes.at(-1), f=frame-s.start;
 c.save();c.globalAlpha=ease(f/22);c.translate(0,18*(1-ease(f/25)));
 text(s.title,72,160,51,t.foreground,600);text(s.subtitle,74,207,23,t.muted);
 if(s.type==='barChart'){
  const rows=p.source.rows,max=Math.max(...rows.map(r=>r[1]),1)*1.12,n=rows.length,step=1090/n,bw=Math.min(180,step*.65);
  for(let i=0;i<4;i++){let y=552-i*85;c.strokeStyle='#2b3b44';c.beginPath();c.moveTo(74,y);c.lineTo(1200,y);c.stroke();}
  rows.forEach((r,i)=>{const a=ease((f-12-i*9)/55),h=r[1]/max*270*a,x=94+i*step;c.fillStyle=i===n-1?t.accent:'#668b7b';c.fillRect(x,552-h,bw,h);text((p.source.valuePrefix??'$')+Number((r[1]*a).toPrecision(5)).toLocaleString('en-US')+(p.source.valueSuffix??'k'),x,532-h,27,t.foreground,600,step-12);text(r[0],x,593,22,t.muted,400,step-12);});
 }else{
  text(s.metric,70,430,s.type==='headline'?174:142,t.accent,600);text(s.metricLabel,80,490,26,t.foreground);if(s.type==='summary'){text('READ THE SIGNAL. KEEP THE SOURCE.',80,569,16,t.muted,600);}
 }
 c.restore();text(p.source.label,74,657,16,t.muted);text(`${String(p.scenes.indexOf(s)+1).padStart(2,'0')} / ${String(p.scenes.length).padStart(2,'0')}`,1130,657,17,t.muted);
 c.fillStyle='#31424b';c.fillRect(0,709,1280,3);c.fillStyle=t.accent;c.fillRect(0,709,1280*clamp(frame/(p.durationFrames-1)),3);
}
const api={validate,render};if(typeof module!=='undefined')module.exports=api;root.Motion=api;
})(typeof window!=='undefined'?window:globalThis);
