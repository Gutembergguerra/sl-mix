import asyncio, subprocess, time, sys, os
from playwright.async_api import async_playwright
BASE='/tmp/claude-0/-home-claude/4129777c-0cf8-5d04-a000-871a28639019/scratchpad/smoke/'
async def main():
    srv = subprocess.Popen([sys.executable,'-m','http.server','8766','--directory','/home/claude/mesa/site'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    time.sleep(1); errs=[]
    try:
        async with async_playwright() as p:
            b = await p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required'])
            ctx = await b.new_context(accept_downloads=True, viewport={'width':400,'height':800})
            page = await ctx.new_page()
            page.on('pageerror', lambda e: errs.append('pageerror: '+str(e)))
            page.on('console', lambda m: errs.append('console.'+m.type+': '+m.text) if m.type=='error' and 'ERR_' not in m.text and 'Failed to load resource' not in m.text else None)
            await page.add_init_script("localStorage.setItem('mesa-view2','compacto')")
            await page.goto('http://localhost:8766/index.html'); await page.wait_for_timeout(500)
            await page.evaluate("document.querySelectorAll('.acc-body').forEach(b=>b.hidden=false);document.getElementById('fileSec').hidden=false;document.getElementById('projSec').hidden=false")
            say=lambda: page.evaluate("document.getElementById('avisos').textContent")
            print('secoes:', await page.evaluate("[...document.querySelectorAll('.jump a')].map(a=>a.textContent).join(' | ')"))
            await page.set_input_files('#inc0', BASE+'voz_desafinada.wav'); await page.wait_for_timeout(800)
            print('carregou:', await say())
            await page.click('text=Afinar a voz'); await page.wait_for_timeout(300)
            print('afinando:', await say())
            await page.wait_for_timeout(2500)
            print('resultado:', await say())
            print('canal 1:', await page.inner_text('#fc0'))
            # desfazer pela secao Edicao
            await page.evaluate("[...document.querySelectorAll('#edSec button')].find(b=>b.textContent==='Desfazer').click()"); await page.wait_for_timeout(200)
            print('desfazer:', await say(), '|', await page.inner_text('#fc0'))
            # so a selecao
            await page.select_option('#tuRange','sel')
            await page.click('text=Afinar a voz'); await page.wait_for_timeout(200)
            print('sem selecao:', await say())
            # MP3 sem internet: mensagem amigavel
            async with page.expect_download(timeout=60000) as dl:
                await page.click('text=Exportar mixagem em WAV')
            d=await dl.value; print('wav ok:', d.suggested_filename)
            await page.click('text=Exportar mixagem em MP3'); await page.wait_for_timeout(6000)
            print('mp3 (sem internet aqui):', await say())
            print('overflow:', await page.evaluate("[document.documentElement.scrollWidth, innerWidth]"))
            # salvar e abrir projeto com os novos controles
            await page.fill('#pjName','Voz'); await page.click('text=Salvar projeto no aparelho'); await page.wait_for_timeout(800)
            print('salvar:', await say())
            await b.close()
    finally: srv.terminate()
    print('ERROS:', '\n'.join(errs) if errs else 'nenhum')
asyncio.run(main())
