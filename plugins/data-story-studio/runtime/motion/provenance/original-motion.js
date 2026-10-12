(function(root){
const clamp=(x)=>Math.max(0,Math.min(1,x));
const ease=x=>1-Math.pow(1-clamp(x),3);
function validate(p){
 if(p.schemaVersion!==1)throw Error('Unsupported schema version');
 if(!Number.isInteger(p.fps)||p.fps<1||p.fps>60)throw Error('fps must be 1–60');
 if(p.width!==1280||p.height!==720)throw Error('Prototype supports 1280×720');
 if(!Number.isInteger(p.durationFrames)||p.durationFrames<1||p.durationFrames>3600)throw Error('Invalid duration');
 let end=0; const ids=new Set();
 for(const s of p.scenes){if(ids.has(s.id))throw Error('Duplicate scene id');ids.add(s.id);if(s.start!==end||!Number.isInteger(s.duration)||s.duration<30)throw Error('Scenes must be contiguous, >=30 frames');if(!['headline','barChart','summary'].includes(s.type))throw Error('Unsupported scene');end+=s.duration;for(const k of ['title','subtitle','metric','metricLabel'])if(s[k]!==undefined&&(typeof s[k]!=='string'||s[k].length>140))throw Error('Invalid '+k);}
 if(end!==p.durationFrames)throw Error('Scene duration mismatch');
 if(p.source.columns.join(',')!=='quarter,revenue,margin'||p.source.rows.length<2||p.source.rows.length>8)throw Error('Expected 2–8 quarter/revenue/margin rows');
 for(const r of p.source.rows)if(typeof r[0]!=='string'||r[0].length>20||!Number.isFinite(r[1])||r[1]<0||!Number.isFinite(r[2])||r[2]<0||r[2]>100)throw Error('Invalid data');
 for(const k of ['background','foreground','accent','muted'])if(!/^#[0-9a-f]{6}$/i.test(p.theme[k]))throw Error('Invalid color');
 return p;
}
function storyboard(csv,base){
 const lines=csv.trim().split(/\r?\n/).map(x=>x.split(',').map(x=>x.trim()));
 if(lines[0].join(',')!=='quarter,revenue,margin')throw Error('CSV header must be quarter,revenue,margin');
 const p=JSON.parse(JSON.stringify(base));p.source.rows=lines.slice(1).map(r=>[r[0],Number(r[1]),Number(r[2])]);validate(p);
 const a=p.source.rows[0],b=p.source.rows.at(-1);if(a[1]===0)throw Error('Starting revenue must be >0 for growth calculation');
 const g=Math.round((b[1]/a[1]-1)*100),m=Math.round((b[2]-a[2])*10)/10;
 p.title='Quarterly performance';p.scenes[0].title=g>=0?'A growing year.':'A changing year.';p.scenes[0].subtitle='A data-driven view of revenue and margin.';p.scenes[0].metric=(g>0?'+':'')+g+'%';p.scenes[0].metricLabel=`revenue growth · ${a[0]} to ${b[0]}`;
 p.scenes[1].title='Revenue, quarter by quarter.';p.scenes[2].title='The full picture.';p.scenes[2].metric=(m>0?'+':'')+m+' pp';p.scenes[2].metricLabel=`gross margin · ${a[2]}% → ${b[2]}%`;p.scenes[2].subtitle=`Revenue changed ${g}%; gross margin changed ${m} percentage points.`;return p;
}
function render(canvas,p,frame){
 const c=canvas.getContext('2d');canvas.width=p.width;canvas.height=p.height;const t=p.theme;
 c.fillStyle=t.background;c.fillRect(0,0,1280,720);
 const text=(str,x,y,size,color=t.foreground,weight=400)=>{c.font=`${weight} ${size}px Arial, sans-serif`;c.fillStyle=color;c.fillText(str,x,y)};
 text('MOTION / DATA STORIES',72,58,16,t.muted,600);text('2026 · DEMO',1090,58,15,t.muted);
 const s=p.scenes.find(s=>frame>=s.start&&frame<s.start+s.duration)||p.scenes.at(-1), f=frame-s.start;
 c.save();c.globalAlpha=ease(f/22);c.translate(0,18*(1-ease(f/25)));
 text(s.title,72,160,51,t.foreground,600);text(s.subtitle,74,207,23,t.muted);
 if(s.type==='barChart'){
  const rows=p.source.rows,max=Math.max(...rows.map(r=>r[1]),1)*1.12,n=rows.length,step=1090/n,bw=Math.min(180,step*.65);
  for(let i=0;i<4;i++){let y=552-i*85;c.strokeStyle='#2b3b44';c.beginPath();c.moveTo(74,y);c.lineTo(1200,y);c.stroke();}
  rows.forEach((r,i)=>{const a=ease((f-12-i*9)/55),h=r[1]/max*270*a,x=94+i*step;c.fillStyle=i===n-1?t.accent:'#668b7b';c.fillRect(x,552-h,bw,h);text((p.source.valuePrefix??'$')+Math.round(r[1]*a)+(p.source.valueSuffix??'k'),x,532-h,27,t.foreground,600);text(r[0],x,593,22,t.muted);});
 }else{
  text(s.metric,70,430,s.type==='headline'?174:142,t.accent,600);text(s.metricLabel,80,490,26,t.foreground);if(s.type==='summary'){text('READ THE SIGNAL. KEEP THE SOURCE.',80,569,16,t.muted,600);}
 }
 c.restore();text(p.source.label,74,657,16,t.muted);text(`${String(p.scenes.indexOf(s)+1).padStart(2,'0')} / ${String(p.scenes.length).padStart(2,'0')}`,1130,657,17,t.muted);
 c.fillStyle='#31424b';c.fillRect(0,709,1280,3);c.fillStyle=t.accent;c.fillRect(0,709,1280*clamp(frame/(p.durationFrames-1)),3);
}
const api={validate,storyboard,render};if(typeof module!=='undefined')module.exports=api;root.Motion=api;
})(typeof window!=='undefined'?window:globalThis);
