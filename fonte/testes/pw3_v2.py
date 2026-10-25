import asyncio, subprocess, time, sys, os, wave, struct, math
from playwright.async_api import async_playwright
BASE='/tmp/claude-0/-home-claude/4129777c-0cf8-5d04-a000-871a28639019/scratchpad/smoke/'
def readwav(path):
    w=wave.open(path,'rb'); n=w.getnframes(); ch=w.getnchannels(); raw=w.readframes(n); w.close()
    data=struct.unpack('<%dh'%(n*ch),raw)
    return [data[i*ch]/32768 for i in range(n)], w.getframerate() if False else None
async def export(page,name):
    async with page.expect_download(timeout=90000) as dl:
        await page.click('text=Exportar mixagem em WAV')
    d=await dl.value; path=BASE+name; await d.save_as(path); return path
def rms(x,a,b):
    seg=x[a:b]; return math.sqrt(sum(v*v for v in seg)/max(1,len(seg)))
async def main():
    srv = subprocess.Popen([sys.executable,'-m','http.server','8767','--directory','/home/claude/mesa/site'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    time.sleep(1); errs=[]
    try:
        async with async_playwright() as p:
            b = await p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required'])
            ctx = await b.new_context(accept_downloads=True, viewport={'width':400,'height':800})
            page = await ctx.new_page()
            page.on('pageerror', lambda e: errs.append('pageerror: '+str(e)))
            page.on('console', lambda m: errs.append('console.'+m.type+': '+m.text) if m.type=='error' and 'Failed to load resource' not in m.text else None)
            await page.add_init_script("localStorage.setItem('mesa-view2','compacto')")
            await page.goto('http://localhost:8767/index.html'); await page.wait_for_timeout(500)
            await page.evaluate("document.querySelectorAll('.acc-body').forEach(b=>b.hidden=false);document.getElementById('fileSec').hidden=false;document.getElementById('projSec').hidden=false")
            say=lambda: page.evaluate("document.getElementById('avisos').textContent")
            print('nav:', await page.evaluate("[...document.querySelectorAll('.jump a')].map(a=>a.textContent).join(' | ')"))
            print('sliders do reverb de voz:', await page.locator('#vrSec input[type=range]').count(), '| botoes:', await page.locator('#vrSec button').count())
            await page.click('#btnDemo'); await page.wait_for_timeout(300)
            # canal 5 (melodia) = indice 4; solo nele para isolar
            await page.select_option('#vrCh','4')
            await page.click('#soc4')
            # exportacao A: sem reverb de voz
            pA=await export(page,'vr_off.wav')
            # liga reverb de voz, nivel 100, compressao desligada
            await page.click('#vron'); print('ligar:', await say())
            await page.evaluate("""()=>{const e=document.getElementById('vrLvl');e.value=100;e.dispatchEvent(new Event('input',{bubbles:true}))}""")
            await page.click('#vrcomp'); print('compressao:', await say(), await page.get_attribute('#vrcomp','aria-pressed'))
            pB=await export(page,'vr_on_nocomp.wav')
            # compressao ligada e forte
            await page.click('#vrcomp')
            await page.evaluate("""()=>{const t=document.getElementById('vrThr');t.value=-40;t.dispatchEvent(new Event('input',{bubbles:true}));const r=document.getElementById('vrRatio');r.value=10;r.dispatchEvent(new Event('input',{bubbles:true}))}""")
            pC=await export(page,'vr_on_comp.wav')
            # toca ao vivo com reverb ligado, sem erros
            await page.click('#btnPlay'); await page.wait_for_timeout(1500)
            print('tocando ao vivo:', await page.inner_text('#btnPlay'), await page.inner_text('#tempo'))
            await page.click('#btnPlay')
            # preset e restaurar
            await page.select_option('#vrPreset','sala'); print('preset:', await say(), '| decay:', await page.get_attribute('#vrDecay','aria-valuetext'))
            await page.click('text=Restaurar os valores do preset'); print('restaurar:', await say(), '| decay:', await page.get_attribute('#vrDecay','aria-valuetext'), '| limiar:', await page.get_attribute('#vrThr','aria-valuetext'))
            # salvar e reabrir projeto com o reverb ligado
            await page.fill('#pjName','Reverb'); await page.click('text=Salvar projeto no aparelho'); await page.wait_for_timeout(1500)
            print('salvar:', await say())
            await page.click('#vron'); print('desliga:', await page.get_attribute('#vron','aria-pressed'))
            await page.click('text=Abrir projeto selecionado'); await page.wait_for_timeout(300)
            await page.click('text=Abrir projeto selecionado'); await page.wait_for_timeout(2000)
            print('reabriu, reverb ligado?', await page.get_attribute('#vron','aria-pressed'), '| canal:', await page.input_value('#vrCh'))
            print('overflow:', await page.evaluate("[document.documentElement.scrollWidth, innerWidth]"))
            await b.close()
    finally: srv.terminate()
    A,_=readwav(pA); B,_=readwav(pB); C,_=readwav(pC)
    sr=44100
    print('duracao s  off/on/comp:', round(len(A)/sr,1), round(len(B)/sr,1), round(len(C)/sr,1))
    print('RMS 1-9s  off/on/comp: %.4f %.4f %.4f' % (rms(A,sr,9*sr),rms(B,sr,9*sr),rms(C,sr,9*sr)))
    print('RMS cauda 10.5-12s off/on/comp: %.5f %.5f %.5f' % (rms(A,int(10.5*sr),12*sr),rms(B,int(10.5*sr),min(len(B),12*sr)),rms(C,int(10.5*sr),min(len(C),12*sr))))
    n=min(len(B),len(C),9*sr)
    diff=math.sqrt(sum((B[i]-C[i])**2 for i in range(sr,n))/(n-sr))
    print('diferenca RMS entre sem e com compressao: %.5f (maior que 0 = o sidechain age)' % diff)
    print('ERROS:', '\n'.join(errs) if errs else 'nenhum')
asyncio.run(main())
