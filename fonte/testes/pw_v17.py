import asyncio, subprocess, time, sys
from playwright.async_api import async_playwright
fails=[]
def ck(n,ok,x=''):
    print(('OK   ' if ok else 'FALHA'),n,x)
    if not ok: fails.append(n)
async def main():
    srv=subprocess.Popen([sys.executable,'-m','http.server','8786','--directory','/home/claude/mesa/site'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1);errs=[]
    async with async_playwright() as p:
        b=await p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required','--use-fake-ui-for-media-stream','--use-fake-device-for-media-stream'])
        c=await b.new_context(viewport={'width':400,'height':800},permissions=['microphone']);pg=await c.new_page()
        pg.on('pageerror',lambda e:errs.append(str(e)))
        say=lambda: pg.evaluate("document.getElementById('avisos').textContent")
        await pg.goto('http://localhost:8787/index.html') if False else await pg.goto('http://localhost:8786/index.html');await pg.wait_for_timeout(300)
        for _ in range(2): await pg.click('#btnAddCh')
        await pg.click('#btnProj');await pg.click('#btnDemo');await pg.wait_for_timeout(900);await pg.click('#projClose')
        # grava no canal 1 com a trilha do canal 2 tocando; registra tudo que o leitor ouviria
        await pg.evaluate("window.__falas=[];new MutationObserver(()=>{window.__falas.push(document.getElementById('avisos').textContent)}).observe(document.getElementById('avisos'),{childList:true,characterData:true,subtree:true})")
        await pg.click('#btnRec');await pg.wait_for_timeout(5500)
        falas=await pg.evaluate("window.__falas")
        ck('gravando',(await pg.inner_text('#btnRec'))=='Parar gravação',await pg.inner_text('#btnRec'))
        ck('nenhum aviso de sinal no limite durante a gravação',not any('sinal no limite' in f for f in falas),str(falas))
        await pg.click('#btnRec');await pg.wait_for_timeout(1200)
        t=await say();ck('gravação concluída fala',('Gravação concluída' in t) or ('concluída' in t),t)
        await c.close();await b.close()
    srv.terminate()
    print('ERROS JS:',errs or 'nenhum');print('FALHAS:',fails or 'nenhuma')
asyncio.run(main())
