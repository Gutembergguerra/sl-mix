import asyncio, subprocess, time, sys, zipfile
from playwright.async_api import async_playwright
import wave, struct, math
def _mkwav(path='/tmp/mix_teste.wav'):
    r=44100;w=wave.open(path,'wb');w.setnchannels(1);w.setsampwidth(2);w.setframerate(r)
    w.writeframes(b''.join(struct.pack('<h',int(12000*math.sin(2*math.pi*440*(i/r))) if (i/r)%2<1.5 else 0) for i in range(r*6)));w.close()
_mkwav()
fails=[]
def ck(n,ok,x=''):
    print(('OK   ' if ok else 'FALHA'),n,x)
    if not ok: fails.append(n)
async def main():
    srv=subprocess.Popen([sys.executable,'-m','http.server','8774','--directory','/home/claude/mesa/site'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1);errs=[]
    async with async_playwright() as p:
        b=await p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required'])
        for name,vp in (('retrato',{'width':400,'height':800}),('desktop',{'width':1200,'height':800})):
            print('==',name)
            c=await b.new_context(viewport=vp,accept_downloads=True);pg=await c.new_page()
            pg.on('pageerror',lambda e:errs.append(str(e)))
            async def say():
                await pg.wait_for_timeout(120);return await pg.evaluate("document.getElementById('avisos').textContent")
            await pg.goto('http://localhost:8774/index.html');await pg.wait_for_timeout(300)
            for _ in range(2): await pg.click('#btnAddCh')
            await pg.select_option('#goSel','files');await pg.wait_for_timeout(200);await pg.click('#btnDemo');await pg.wait_for_timeout(700);await pg.click('#projClose')
            btn=pg.locator('[aria-label="Canal 1, editar áudio"]:visible').first
            ck('botão editar áudio visível',await btn.count()==1)
            await btn.click();await pg.wait_for_timeout(200)
            ck('abre tela',await pg.is_visible('#edLayer'));ck('foco título',await pg.evaluate('document.activeElement.id')=='edTitle')
            ck('só a pista escolhida (select edCh)',await pg.input_value('#edCh')=='0')
            ck('inert main',await pg.evaluate("document.getElementById('main').inert"))
            # campos início/fim e passos
            await pg.fill('#edA','2');await pg.press('#edA','Tab');await pg.fill('#edB','4');await pg.press('#edB','Tab')
            ck('seleção',('Duração 2,0' in await say()),await say())
            await pg.click('text=Fim: avançar');t=await say();ck('fim avança',('4 segundos e 100' in t) or ('Fim em 4' in t),t)
            await pg.click('text=Ouvir trecho');ck('ouvir',('Tocando' in await say()))
            await pg.click('button:text-is("Cortar")');ck('cortou','Corte feito' in await say(),await say())
            await pg.click('button:text-is("Desfazer")');ck('desfez','Desfeito' in await say())
            # tocar na tela e pausar
            await pg.click('#edPlay');await pg.wait_for_timeout(1500);await pg.click('#edPlay');await pg.wait_for_timeout(200)
            # marcar divisões
            await pg.click('text=Marcar divisão aqui');ck('divisão 1','Divisão 1 marcada' in await say(),await say())
            await pg.evaluate("document.getElementById('edPlay').click()");await pg.wait_for_timeout(1200);await pg.evaluate("document.getElementById('edPlay').click()")
            await pg.click('text=Marcar divisão aqui');ck('divisão 2','Divisão 2' in await say(),await say())
            await pg.click('text=Ouvir antes e depois da divisão');ck('ouvir divisão','Ouvindo' in await say())
            await pg.click('text=Ajustar divisão ao silêncio');print('  ',await say())
            async with pg.expect_download() as d: await pg.click('text=Salvar faixas em ZIP')
            dl=await d.value;await dl.save_as('/tmp/f.zip');z=zipfile.ZipFile('/tmp/f.zip');ck('zip faixas',z.testzip() is None and len(z.namelist())==3,str(z.namelist()))
            await pg.fill('#cutSil','0.5');await pg.click('text=Achar divisões por silêncio');print('  ',await say())
            # trocar de canal e colocar arquivo no cursor
            await pg.select_option('#edCh','2');await pg.wait_for_timeout(100)
            ck('titulo trocou','Canal 3' in await pg.inner_text('#edTitle'))
            await pg.click('text=Excluir todo o áudio do canal');await pg.click('text=Excluir todo o áudio do canal');ck('excluiu','esvaziado' in await say(),await say())
            async with pg.expect_file_chooser() as fc: await pg.click('text=Colocar arquivo a partir do cursor')
            f=await fc.value;await f.set_files('/tmp/mix_teste.wav');await pg.wait_for_timeout(1500)
            ck('colocou arquivo','colocado' in await say(),await say())
            async with pg.expect_file_chooser() as fc: await pg.click('text=Inserir arquivo no cursor')
            f=await fc.value;await f.set_files('/tmp/mix_teste.wav');await pg.wait_for_timeout(1500)
            ck('inseriu arquivo','inserido' in await say(),await say())
            await pg.keyboard.press('Escape');await pg.wait_for_timeout(150)
            ck('fecha com Esc',not await pg.is_visible('#edLayer'));ck('foco volta',await pg.evaluate("document.activeElement.getAttribute('aria-label')")=='Canal 3, editar áudio',await pg.evaluate("document.activeElement.getAttribute('aria-label')"))
            ov=await pg.evaluate("[document.documentElement.scrollWidth,innerWidth]");ck('sem rolagem lateral',ov[0]<=ov[1],str(ov))
            await pg.select_option('#viewSel','faixas');ck('botão Editar na faixa',await pg.locator('[aria-label="Canal 1, editar áudio"]:visible').count()==1)
    print('ERROS JS:',errs or 'nenhum');print('FALHAS:',fails or 'nenhuma');srv.kill()
asyncio.run(main())
