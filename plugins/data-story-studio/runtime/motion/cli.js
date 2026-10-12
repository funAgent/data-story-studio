#!/usr/bin/env node
'use strict';
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),{spawn,spawnSync}=require('node:child_process');
const M=require('./motion');
const MARK='.data-story-motion-project.json';
function assertPath(p){
 if(typeof p!=='string'||!path.isAbsolute(p)||p.split(/[\\/]/).includes('..'))throw Error('Use an absolute path with no traversal');
 const resolved=path.resolve(p),parts=resolved.slice(path.parse(resolved).root.length).split(path.sep);let at=path.parse(resolved).root;
 for(const part of parts){at=path.join(at,part);try{if(fs.lstatSync(at).isSymbolicLink())throw Error('Symlinks are not allowed');}catch(e){if(e.code!=='ENOENT')throw e;}}
 return resolved;
}
function outsideRuntime(p){
 assertPath(p);const parts=p.split(path.sep);if(parts.some(s=>s==='.data-story-runtime'||s==='.codex'||s==='node_modules'))throw Error('Project/output must not be in runtime, dependency or Codex cache directories');
 let at=__dirname;while(at!==path.dirname(at)){if(fs.existsSync(path.join(at,'.codex-plugin'))&& (p===at||p.startsWith(at+path.sep)))throw Error('Outputs cannot be in the plugin');at=path.dirname(at);}
 if(p===__dirname||p.startsWith(__dirname+path.sep))throw Error('Outputs cannot be in the runtime');
}
function readJSON(p){assertPath(p);const st=fs.lstatSync(p);if(!st.isFile()||st.size>2*1024*1024)throw Error('JSON must be a regular file at most 2 MiB');return JSON.parse(fs.readFileSync(p,'utf8'));}
function name(n,ext){if(!/^[A-Za-z0-9][A-Za-z0-9._-]{0,79}$/.test(n)||n.includes('..')||!n.endsWith(ext))throw Error('Invalid output/project filename');return n;}
function exclusive(p,data){assertPath(p);fs.writeFileSync(p,data,{flag:'wx'});}
function projectDir(p){p=assertPath(p);outsideRuntime(p);if(readJSON(path.join(p,MARK)).format!=='data-story-motion-project-v1')throw Error('Not a marked motion project');return p;}
function aggregateSnapshot(s,index){
 if(!s||s.schema_version!==1||!Array.isArray(s.rows)||s.rows.length<1||s.rows.length>10000||!Array.isArray(s.charts)||!Array.isArray(s.metrics)||!Array.isArray(s.dimensions))throw Error('Invalid snapshot contract or row limit (1..10000)');
 const c=s.charts[index];if(!c||!['bar','line','table'].includes(c.type)||!s.dimensions.includes(c.dimension))throw Error('Invalid selected chart');
 const matches=s.metrics.filter(m=>m.id===c.metric);if(matches.length!==1)throw Error('Metric id must resolve uniquely');const m=matches[0];
 if(!['sum','mean','count'].includes(m.aggregation)||typeof m.field!=='string')throw Error('Invalid aggregation');
 const groups=new Map();for(const r of s.rows){if(!r||typeof r!=='object'||Array.isArray(r)||!Object.hasOwn(r,c.dimension))throw Error('Missing dimension');const key=r[c.dimension];
 if(typeof key!=='string'||!key||key.length>20||/[\u0000-\u001f]/.test(key))throw Error('Dimension must contain nonempty strings <=20 characters');
 if(!Object.hasOwn(r,m.field))throw Error('Missing selected metric field');let g=groups.get(key)||{sum:0,count:0};const v=r[m.field];if(v!==null&&v!==undefined){
 if(m.aggregation!=='count'){if(!Number.isFinite(v)||v<0||v>1e12)throw Error('Non-null metric must be finite, nonnegative, <=1e12');g.sum+=v;if(!Number.isFinite(g.sum)||g.sum>1e12)throw Error('Aggregated value exceeds 1e12 limit');}g.count++;}groups.set(key,g);}
 if(['sum','mean'].includes(m.aggregation)&&[...groups.values()].some(g=>g.count===0))throw Error('Cannot render a category with all-null '+m.aggregation);
 if(groups.size<2||groups.size>8)throw Error('Motion supports 2..8 categories; no truncation is performed');
 if(!s.provenance||typeof s.provenance.sha256!=='string'||!/^[a-f0-9]{64}$/.test(s.provenance.sha256)||s.provenance.row_count!==s.rows.length)throw Error('Invalid snapshot provenance/hash/row_count');
 return {rows:[...groups].map(([k,g])=>[k,m.aggregation==='count'?g.count:m.aggregation==='mean'?g.sum/g.count:g.sum]),chart:c,metric:m,warnings:[...(c.type!=='bar'?[`Selected ${c.type} chart represented as bars; original retained.`]:[]),'Category order follows first appearance; values are displayed with 5 significant digits.','count counts non-null metric cells; sum and mean skip null cells; all-null sum/mean categories and missing fields are rejected.']};
}
async function encode(p,output,format,frame){
 const {createCanvas}=require('@napi-rs/canvas');const canvas=createCanvas(p.width,p.height);
 if(format==='png'){M.render(canvas,p,frame);exclusive(output,canvas.toBuffer('image/png'));return;}
 const tmp=fs.mkdtempSync(path.join(path.dirname(output),'.render-'));const tmpfile=path.join(tmp,'render.mp4');let enc;
 try{enc=spawn('ffmpeg',['-n','-loglevel','error','-f','rawvideo','-pixel_format','rgba','-video_size',`${p.width}x${p.height}`,'-framerate',String(p.fps),'-i','pipe:0','-c:v','libx264','-preset','fast','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart','-an',tmpfile],{stdio:['pipe','ignore','pipe'],shell:false});
 let stderr='';enc.stderr.on('data',d=>{stderr=(stderr+d).slice(-8192)});let failed;
 const done=new Promise((resolve,reject)=>{enc.on('error',reject);enc.on('close',code=>code===0?resolve():reject(Error(stderr||`FFmpeg exited ${code}`)))});done.catch(e=>{failed=e});enc.stdin.on('error',()=>{});
 const timer=setTimeout(()=>enc.kill('SIGKILL'),300000);
 try{for(let f=0;f<p.durationFrames;f++){if(failed)throw failed;M.render(canvas,p,f);const bytes=Buffer.from(canvas.getContext('2d').getImageData(0,0,p.width,p.height).data);await new Promise((resolve,reject)=>enc.stdin.write(bytes,e=>e?reject(e):resolve()));}enc.stdin.end();await done;}finally{clearTimeout(timer);if(enc.exitCode===null)enc.kill('SIGKILL');}
 // A hard link atomically refuses an existing target; FFmpeg never writes the final path.
 assertPath(output);fs.linkSync(tmpfile,output);
 }finally{fs.rmSync(tmp,{recursive:true,force:true});}
}
async function main(argv){const command=argv.shift(),args={};while(argv.length){const k=argv.shift();if(!k.startsWith('--')||!argv.length||Object.hasOwn(args,k))throw Error('Expected unique --option value pairs');args[k]=argv.shift();}
 const allowed={'doctor':[],'init':['--project-dir'],'import-snapshot':['--project-dir','--input','--chart','--output','--duration-seconds'],'render':['--project-dir','--project','--format','--output','--frame'],'validate':['--project-dir','--project']};if(!allowed[command])throw Error('Commands: doctor, init, import-snapshot, validate, render');for(const k of Object.keys(args))if(!allowed[command].includes(k))throw Error('Unknown option '+k);
 if(command==='doctor'){let canvas;try{const mod=require('@napi-rs/canvas');canvas={available:true,version:require('@napi-rs/canvas/package.json').version,fontFamilies:mod.GlobalFonts.families.map(f=>f.family).filter(f=>/Arial|Liberation Sans|Noto Sans CJK/i.test(f))};}catch(e){canvas={available:false,error:e.message}}const binary=n=>{const r=spawnSync(n,['-version'],{encoding:'utf8',timeout:5000});return {available:r.status===0,version:r.stdout?.split('\n')[0]||r.error?.message||r.stderr?.slice(0,200)}};const report={node:process.version,canvas,ffmpeg:binary('ffmpeg'),ffprobe:binary('ffprobe'),fontNote:'Uses installed Liberation Sans / Arial / Noto Sans CJK SC fallbacks. Glyph coverage and exact pixels depend on installed fonts.'};console.log(JSON.stringify(report,null,2));if(!canvas.available||!report.ffmpeg.available)process.exitCode=1;return;}
 if(command==='init'){const dest=assertPath(args['--project-dir']);outsideRuntime(dest);if(fs.existsSync(dest))throw Error('init requires a new directory');assertPath(path.dirname(dest));fs.mkdirSync(dest);exclusive(path.join(dest,MARK),JSON.stringify({format:'data-story-motion-project-v1'}));exclusive(path.join(dest,'project.json'),fs.readFileSync(path.join(__dirname,'samples/project.json')));console.log(JSON.stringify({projectDir:dest,project:'project.json'}));return;}
 const dir=projectDir(args['--project-dir']);
 if(command==='import-snapshot'){const input=assertPath(args['--input']),snapshot=readJSON(input),index=Number(args['--chart']??0);if(!Number.isInteger(index)||index<0)throw Error('Invalid chart index');const a=aggregateSnapshot(snapshot,index),p=readJSON(path.join(__dirname,'samples/project.json'));p.title=typeof snapshot.title==='string'?snapshot.title:'Dashboard snapshot';p.source={columns:['category','value'],rows:a.rows,label:'Frozen dashboard snapshot · original source retained',valuePrefix:'',valueSuffix:''};const seconds=Number(args['--duration-seconds']??8);if(!Number.isFinite(seconds)||seconds<1||seconds>60||!Number.isInteger(seconds*p.fps))throw Error('duration-seconds must give 30..1800 whole frames at 30fps');p.durationFrames=seconds*p.fps;p.scenes=[{id:'snapshot-bars',type:'barChart',start:0,duration:p.durationFrames,title:p.title,subtitle:`${a.metric.aggregation}(${a.metric.field}) by ${a.chart.dimension}`}];p.snapshot={sha256:crypto.createHash('sha256').update(fs.readFileSync(input)).digest('hex'),original:snapshot,selectedChart:index,aggregation:a.metric,warnings:a.warnings};M.validate(p);const out=path.join(dir,name(args['--output']||'snapshot-project.json','.json'));exclusive(out,JSON.stringify(p,null,2)+'\n');console.log(JSON.stringify({output:out,warnings:a.warnings}));return;}
 const p=M.validate(readJSON(path.join(dir,name(args['--project']||'project.json','.json'))));if(command==='validate'){console.log(JSON.stringify({valid:true,scenes:p.scenes.length,frames:p.durationFrames}));return;}
 const format=args['--format']||'png';if(!['png','mp4'].includes(format))throw Error('format must be png or mp4');const frame=Number(args['--frame']??Math.min(100,p.durationFrames-1));if(!Number.isInteger(frame)||frame<0||frame>=p.durationFrames)throw Error('frame outside project');const output=path.join(dir,name(args['--output']||`preview.${format}`,'.'+format)),metadata=output+'.metadata.json';assertPath(output);assertPath(metadata);if(fs.existsSync(metadata))throw Error('Metadata exists; choose a fresh output filename');if(fs.existsSync(output))throw Error('Output exists; choose a fresh filename');await encode(p,output,format,frame);const hash=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');exclusive(metadata,JSON.stringify({project_sha256:hash(fs.readFileSync(path.join(dir,args['--project']||'project.json'))),output_sha256:hash(fs.readFileSync(output)),rendered_at:new Date().toISOString(),format,width:p.width,height:p.height,fps:p.fps,project_duration_seconds:p.durationFrames/p.fps,rendered_frames:format==='mp4'?p.durationFrames:1,selected_frame:format==='png'?frame:null},null,2)+'\n');console.log(JSON.stringify({output,metadata,format,frames:format==='mp4'?p.durationFrames:1}));
}
if(require.main===module)main(process.argv.slice(2)).catch(e=>{console.error(e.message);process.exitCode=1});
module.exports={aggregateSnapshot,assertPath,main};
