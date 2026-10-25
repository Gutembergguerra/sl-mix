const fs=require('fs');
const s=fs.readFileSync('app-body.html','utf8');
const m=s.match(/\/\*PURE-START\*\/([\s\S]*?)\/\*PURE-END\*\//)[1];
const api=new Function(m+';return {pExtract,pCut,pPaste,pSilence,pTrim,pShift,pSplice,pSnap,encodeWav,makeCurve,fadeLen,softJoin}')();
const assert=require('assert');
const sr=8000;
const ramp=n=>Float32Array.from({length:n},(_,i)=>1);
let D=[ramp(8000)];
// cut 2000..4000
let c=api.pCut(D,2000,4000,sr);
assert.equal(c[0].length,6000);
assert(c[0][0]===1 && c[0][1000]===1);
assert(c[0][1999]===0 || Math.abs(c[0][1999])<0.1, 'join dip '+c[0][1999]);
assert(c[0][2000]<0.1);
// paste
let clip=api.pExtract(D,0,1000);
let p=api.pPaste(D,4000,clip,sr);
assert.equal(p[0].length,9000);
// paste into empty at 500
let pe=api.pPaste(null,500,clip,sr);
assert.equal(pe[0].length,1500); assert.equal(pe[0][100],0);
// paste stereo-mono mix
let st=api.pPaste([ramp(100),ramp(100)],50,[ramp(10)],sr);
assert.equal(st.length,2); assert.equal(st[1].length,110);
// silence
let sl=api.pSilence(D,1000,2000,sr);
assert.equal(sl[0].length,8000); assert.equal(sl[0][1500],0); assert.equal(sl[0][999],1); assert(sl[0][1000]>0.5);
// trim
let tr=api.pTrim(D,1000,3000,sr);
assert.equal(tr[0].length,2000); assert(tr[0][0]<0.1); assert.equal(tr[0][1000],1);
// shift
assert.equal(api.pShift(D,100)[0].length,8100);
assert.equal(api.pShift(D,-100)[0].length,7900);
assert.equal(api.pShift(D,-9000),null);
// splice onto empty at 1s
let rec=ramp(2000);
let sp=api.pSplice(null,8000,rec,sr);
assert.equal(sp[0].length,10000); assert.equal(sp[0][100],0);
// splice inside existing
let sp2=api.pSplice([ramp(8000)],1000,rec,sr);
assert.equal(sp2[0].length,8000);
let sp3=api.pSplice([ramp(8000)],7000,rec,sr);
assert.equal(sp3[0].length,9000);
// snap: loud signal with a quiet gap at 0.5s
let sig=new Float32Array(16000).fill(0.5);
for(let i=8000+400;i<8000+400+200;i++)sig[i]=0;
let sn=api.pSnap(sig,8000,8000);
assert(Math.abs(sn-8500)<200,'snap '+sn);
// wav
let w=api.encodeWav([new Float32Array(10),new Float32Array(10)],44100);
assert.equal(w.byteLength,44+10*2*2);
// curve
let cv=api.makeCurve(0); assert(Math.abs(cv[512]-0.0)<0.01 && Math.abs(cv[1023]-1)<1e-6 && Math.abs(cv[0]+1)<1e-6);
let cv2=api.makeCurve(1); assert(cv2[700]>cv[700]);
console.log('PURE TESTS OK');

// --- projetos ---
const api2=new Function(fs.readFileSync('app-body.html','utf8').match(/\/\*PURE-START\*\/([\s\S]*?)\/\*PURE-END\*\//)[1]+';return {toI16,fromI16,packProject,unpackProject}')();
const f32=Float32Array.from([0,0.5,-0.5,1,-1,0.25,2,-2]);
const i16=api2.toI16(f32);
assert.equal(i16[3],32767);assert.equal(i16[4],-32768);assert.equal(i16[6],32767);assert.equal(i16[7],-32768);
const back=api2.fromI16(i16);
for(let i=0;i<5;i++)assert(Math.abs(back[i]-Math.max(-1,Math.min(1,f32[i])))<1e-4,'roundtrip '+i);
const L=Int16Array.from({length:101},(_,i)=>i*10),R2=Int16Array.from({length:101},(_,i)=>-i*10);
const chs=[null,{sr:44100,pcm:[L,R2],name:'Gravação à noite ç',edited:true},null,{sr:48000,pcm:[Int16Array.from([1,2,3])],name:'x',edited:false},null,null];
const meta={name:'Meu projeto ção',savedAt:1,secs:2,sliders:{a:1},selects:{},toggles:{b:true}};
const ab=api2.packProject(meta,chs);
const un=api2.unpackProject(ab);
assert.equal(un.meta.name,'Meu projeto ção');
assert.equal(un.chs.length,6);assert.equal(un.chs[0],null);
assert.equal(un.chs[1].pcm.length,2);assert.equal(un.chs[1].pcm[0][100],1000);assert.equal(un.chs[1].pcm[1][100],-1000);
assert.equal(un.chs[1].name,'Gravação à noite ç');assert.equal(un.chs[1].edited,true);
assert.equal(un.chs[3].sr,48000);assert.deepEqual(Array.from(un.chs[3].pcm[0]),[1,2,3]);
assert.equal(api2.unpackProject(new ArrayBuffer(20)),null);
assert.throws(()=>api2.unpackProject(ab.slice(0,ab.byteLength-50)));
console.log('PROJECT TESTS OK');

// --- reverb de voz ---
(()=>{
  const src=fs.readFileSync('app-body.html','utf8');
  const pure=src.match(/\/\*PURE-START\*\/([\s\S]*?)\/\*PURE-END\*\//)[1];
  const V=new Function(pure+';return {DUCK_CODE,hallIRData}')();
  // ducker: carrega a classe com stubs
  let Cls=null;
  new Function('AudioWorkletProcessor','registerProcessor','sampleRate',V.DUCK_CODE)(class{},(n,c)=>{Cls=c},44100);
  const p=new Cls();
  const par={thr:[-18],ratio:[3],att:[.005],rel:[.18]};
  const blk=(v)=>[Float32Array.from({length:128},()=>v)];
  const run=(keyV,n)=>{let o;for(let i=0;i<n;i++){const out=[new Float32Array(128),new Float32Array(128)];p.process([[...blk(1),...blk(1)],keyV===null?[]:blk(keyV)],[out],par);o=out}return o};
  const o0=run(0,50);assert(Math.abs(o0[0][127]-1)<1e-6,'sem chave: ganho 1, veio '+o0[0][127]);
  const o1=run(1,400);const g=o1[0][127];
  assert(Math.abs(g-Math.pow(10,-12/20))<0.01,'chave 0 dBFS: ganho ~0.251, veio '+g);
  const o2=run(0,400);assert(o2[0][127]>.95,'solta depois: '+o2[0][127]);
  const o3=run(null,10);assert(Math.abs(o3[0][127]-1)<1e-6);
  par.ratio=[1];const o4=run(1,400);assert(Math.abs(o4[0][127]-1)<1e-6,'ratio 1 = sem compressao');
  // IR do reverb
  const d=V.hallIRData(44100,2.8,85);
  assert.equal(d.length,2);assert.equal(d[0].length,Math.floor(2.8*1.15*44100));
  let nan=0,e1=0,e2=0;for(let i=0;i<d[0].length;i++){if(!isFinite(d[0][i]))nan++;if(i<44100)e1+=d[0][i]**2;else if(i<2*44100)e2+=d[0][i]**2}
  assert.equal(nan,0);assert(e1>e2*2,'decai: '+e1+' vs '+e2);
  console.log('VOICE REVERB TESTS OK');
})();

/* v1.1: zip, split, silences */
{
  const a3=new Function(fs.readFileSync('app-body.html','utf8').match(/\/\*PURE-START\*\/([\s\S]*?)\/\*PURE-END\*\//)[1]+';return {crc32,makeZip,pSegments,pFindSilences}')();
  assert.equal(a3.crc32(new TextEncoder().encode('123456789')),0xCBF43926);
  assert.deepEqual(a3.pSegments(100,[30,60]),[[0,30],[30,60],[60,100]]);
  assert.deepEqual(a3.pSegments(100,[0,100,50,50]),[[0,50],[50,100]]);
  const sr=1000,x=new Float32Array(5000).fill(0);
  for(let i=0;i<1000;i++)x[i]=.5;for(let i=3000;i<5000;i++)x[i]=.5;
  const p=a3.pFindSilences(x,sr,1,-45);
  assert.equal(p.length,1);assert(p[0]>1900&&p[0]<2100);
  assert.equal(a3.pFindSilences(x,sr,3,-45).length,0);
  const z=a3.makeZip([{name:'a.wav',data:new Uint8Array([1,2,3])},{name:'b ç.wav',data:new Uint8Array([9])}]);
  fs.writeFileSync(process.env.ZIPOUT||'/tmp/t.zip',z);
  console.log('V11 TESTS OK');
}
