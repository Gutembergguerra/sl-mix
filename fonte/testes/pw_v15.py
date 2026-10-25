import asyncio, subprocess, time, sys, wave, struct, math
from playwright.async_api import async_playwright
fails=[]
def ck(n,ok,x=''):
    print(('OK   ' if ok else 'FALHA'),n,x)
    if not ok: fails.append(n)
def mkwav(path):
    r=44100;w=wave.open(path,'wb');w.setnchannels(1);w.setsampwidth(2);w.setframerate(r)
    w.writeframes(b''.join(struct.pack('<h',int(9000*math.sin(2*math.pi*452*(i/r)))) for i in range(r*3)));w.close()
async def main():
    mkwav('/tmp/voz_teste.wav')
    srv=subprocess.Popen([sys.executable,'-m','http.server','8784','--directory','/home/claude/mesa/site'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1);errs=[]
    async with async_playwright() as p:
        b=await p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required'])
        pg=await (await b.new_context(viewport={'width':400,'height':800})).new_page()
        pg.on('pageerror',lambda e:errs.append(str(e)))
        say=lambda: pg.evaluate("document.getElementById('avisos').textContent")
        await pg.goto('http://localhost:8784/index.html');await pg.wait_for_timeout(300)
        for _ in range(2): await pg.click('#btnAddCh')
        await pg.set_input_files('#inc1','/tmp/voz_teste.wav');await pg.wait_for_timeout(1200)
        await pg.evaluate("(()=>{const sec=document.querySelector('[data-ch=\"1\"]');Array.from(sec.querySelectorAll('button')).find(x=>x.offsetParent!==null&&/, efeitos$/.test(x.getAttribute('aria-label')||'')).click()})()");await pg.wait_for_timeout(250)
        await pg.click('#fxBody > details.fx:has(summary[aria-label$="afinação de voz"]) > summary')
        ck('afinação vale para o canal 2',await pg.input_value('#tuCh')=='1')
        await pg.click('#fxBody button:text-is("Afinar a voz")');await pg.wait_for_timeout(3500)
        t=await say();ck('afinou o canal 2',('Afinação aplicada' in t) or ('já está dentro' in t),t)
        await pg.click('#fxClose');await pg.wait_for_timeout(200)
        await b.close()
    srv.terminate()
    print('ERROS JS:',errs or 'nenhum');print('FALHAS:',fails or 'nenhuma')
asyncio.run(main())
