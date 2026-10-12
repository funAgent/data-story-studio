'use strict';
// Minimal DOM adapter: tests real generated inline logic. Not a browser/layout test.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const file=process.argv[2];if(!file)throw Error('Usage: node tests/test_dashboard_dom.js /ABS/dashboard/index.html');
const html=fs.readFileSync(file,'utf8');const chunks=[...html.matchAll(/<script([^>]*)>([\s\S]*?)<\/script>/g)];assert.equal(chunks.length,2,'Expected JSON data plus one executable script');
class Element{
 constructor(tag){this.tag=tag;this.children=[];this.attributes={};this.events={};this.style={};this._text='';this._value=undefined;this._selectedIndex=0;}
 set textContent(v){this._text=String(v);this.children=[]}get textContent(){return this._text+this.children.map(c=>c.textContent).join('')}
 append(...v){this.children.push(...v)}replaceChildren(...v){this.children=v;this._text=''}setAttribute(k,v){this.attributes[k]=v}addEventListener(k,f){this.events[k]=f}
 get selectedIndex(){return this._selectedIndex}set selectedIndex(i){this._selectedIndex=i;this._value=undefined}
 get value(){return this._value??(this.tag==='select'?this.children[this._selectedIndex]?.value??'':'')}set value(v){this._value=String(v)}
}
const ids={};for(const name of ['title','provenance','dimension','metric','filter-field','filter-value','status','cards','charts','reset','snapshot'])ids[name]=new Element(['dimension','metric','filter-field'].includes(name)?'select':'div');
ids.snapshot.textContent=chunks[0][2];const data=JSON.parse(chunks[0][2]);const document={getElementById:id=>ids[id],createElement:t=>new Element(t),createElementNS:(ns,t)=>new Element(t),title:''};
const context=vm.createContext({document,Intl,Map,JSON,Number,String,Math});vm.runInContext(chunks[1][2],context,{timeout:3000});
assert.equal(document.title,data.title);assert.equal(ids.charts.children.length,data.charts.length);assert.equal(ids.status.textContent,`${data.rows.length.toLocaleString()} of ${data.rows.length.toLocaleString()} rows`);
const filter=data.dimensions[0],needle=String(data.rows[0][filter]);ids['filter-field'].value=filter;ids['filter-value'].value=needle;ids['filter-value'].events.input();const expected=data.rows.filter(r=>String(r[filter]??'').toLocaleLowerCase().includes(needle.toLocaleLowerCase())).length;assert.equal(ids.status.textContent,`${expected.toLocaleString()} of ${data.rows.length.toLocaleString()} rows`);
ids['filter-value'].value='NO_MATCH_7ca58f1e';ids['filter-value'].events.input();assert.equal(ids.status.textContent,`0 of ${data.rows.length.toLocaleString()} rows`);assert.ok(ids.charts.children.every(s=>s.textContent.includes('No rows match')));
ids.reset.events.click();assert.equal(ids.status.textContent,`${data.rows.length.toLocaleString()} of ${data.rows.length.toLocaleString()} rows`);
ids.dimension.value=data.dimensions.at(-1);ids.dimension.events.change();assert.ok(ids.charts.children.every(c=>c.children[0].textContent.endsWith('by '+data.dimensions.at(-1))));
ids.metric.value=data.metrics.at(-1).id;ids.metric.events.change();assert.ok(ids.charts.children.every(c=>c.children[0].textContent.startsWith(data.metrics.at(-1).aggregation+' of '+data.metrics.at(-1).field)));
ids.reset.events.click();assert.equal(ids.charts.children.length,data.charts.length);
console.log(JSON.stringify({passed:true,checks:['generated script execution','chart/card creation','substring filter','empty results','reset','dimension selection','metric selection','repeat reset'],limitation:'Minimal DOM adapter; no browser layout, accessibility tree or screenshot validation.'},null,2));
