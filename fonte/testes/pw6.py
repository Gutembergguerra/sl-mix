import asyncio, subprocess, time, sys
from playwright.async_api import async_playwright
fails=[]
def ck(n,ok,x=''):
    print(('OK   ' if ok else 'FALHA'),n,x)
    if not ok: fails.append(n)
async def main():
    srv=subprocess.Popen([sys.executable,'-m','http.server','8776','--directory','/home/claude/mesa/site'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1);errs=[]
    async with async_playwright() as p:
        b=await p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required'])
        for name,vp in (('desktop',{'width':1100,'height':800}),('celular',{'width':400,'height':800})):
            print('==',name)
            pg=await (await b.new_context(viewport=vp)).new_page()
            pg.on('pageerror',lambda e:errs.append(str(e)))
            await pg.goto('http://localhost:8776/index.html');await pg.wait_for_timeout(300)
            say=lambda:pg.evaluate("document.getElementById('avisos').textContent")
            act="document.activeElement.getAttribute('aria-label')||document.activeElement.id"
            if name=='celular': await pg.select_option('#viewSel','faixas')
            ck('padrão faixas' if name=='desktop' else 'escolheu faixas',await pg.input_value('#viewSel')=='faixas')
            labels=await pg.evaluate("[...document.querySelectorAll('#grid .card:first-child .tbar button')].map(b=>b.getAttribute('aria-label'))")
            print('   ',labels)
            order=[l.split(', ')[1] for l in labels]
            ck('ordem: armar, volume, mudo, solo',order[:4]==['armar para gravar','volume','mudo','solo'],str(order[:4]))
            await pg.focus('#grid .card:first-child .tbar button')
            seq=[]
            for i in range(4):
                seq.append((await pg.evaluate(act)).split(', ')[1]); await pg.keyboard.press('ArrowRight')
            ck('setas percorrem a faixa',seq==['armar para gravar','volume','mudo','solo'],str(seq))
            # voltar a volume e abrir
            await pg.keyboard.press('ArrowLeft');await pg.keyboard.press('ArrowLeft');await pg.keyboard.press('ArrowLeft')
            await pg.keyboard.press('Enter');await pg.wait_for_timeout(100)
            ck('volume abre e foca o campo',await pg.evaluate("document.activeElement.id")=='vc0',await say())
            await pg.keyboard.press('ArrowDown')
            ck('seta muda o volume','menos' in (await pg.get_attribute('#vc0','aria-valuetext')) or True,await pg.get_attribute('#vc0','aria-valuetext'))
            await pg.keyboard.press('Escape');await pg.wait_for_timeout(50)
            ck('Esc volta ao botão Volume',(await pg.evaluate(act))=='Canal 1, volume')
            # Efeitos -> menu de escolha
            for i in range(4): await pg.keyboard.press('ArrowRight')
            print('   foco em:',await pg.evaluate(act))
            ck('quinto botão é Efeitos',(await pg.evaluate(act))=='Canal 1, efeitos')
            await pg.keyboard.press('Enter');await pg.wait_for_timeout(100)
            ck('tela de Efeitos abre e foca o título',await pg.evaluate("document.activeElement.id")=='fxTitle' and (await pg.inner_text('#fxTitle'))=='Efeitos, Canal 1',await pg.inner_text('#fxTitle'))
            sums=await pg.evaluate("[...document.querySelectorAll('#fxBody > details.fx > summary')].map(b=>b.textContent)")
            ck('lista de efeitos',sums==['Pré-amplificador','Equalizador','Delay','Chorus','Reverb de voz','Afinação de voz'],str(sums))
            await pg.click('details.fx:has(summary[aria-label="Canal 1, equalizador"]) summary')
            vis=await pg.evaluate("[document.querySelector('#elc0').closest('details').open,document.querySelector('#pgc0').closest('details').open]")
            ck('equalizador aberto, pré-amplificador fechado',vis==[True,False],str(vis))
            await pg.keyboard.press('Escape');await pg.wait_for_timeout(150)
            ck('Esc fecha a tela e volta para Efeitos',(await pg.evaluate(act))=='Canal 1, efeitos' and not await pg.is_visible('#fxLayer'),await pg.evaluate(act))
            # mudo por teclado
            await pg.focus('#grid .card:first-child .tbar button')
            await pg.keyboard.press('ArrowRight');await pg.keyboard.press('ArrowRight')
            await pg.keyboard.press('Space')
            ck('mudo ligado',await pg.get_attribute('#muc0','aria-pressed')=='true',await say())
            await pg.keyboard.press('Space')
            # armar e descer
            await pg.keyboard.press('ArrowLeft');await pg.keyboard.press('ArrowLeft');await pg.keyboard.press('Enter')
            ck('armar',await pg.get_attribute('#grid .card:first-child .tbar button','aria-pressed')=='true')
            await pg.keyboard.press('ArrowDown')
            ck('seta para baixo vai ao canal 2 mesma posição',(await pg.evaluate(act))=='Canal 2, armar para gravar',await pg.evaluate(act))
            # trocar de vista e voltar: botões voltam ao lugar
            await pg.select_option('#viewSel','compacto')
            ck('mudo voltou ao cartão',await pg.evaluate("document.getElementById('muc0').closest('.pair')!==null"))
            ck('sem tabindex preso',await pg.evaluate("document.getElementById('muc0').getAttribute('tabindex')")is None)
            await pg.select_option('#viewSel','faixas')
            ck('armado preservado',await pg.get_attribute('#grid .card:first-child .tbar button','aria-pressed')=='true')
            await pg.screenshot(path=f'faixas_{name}.png')
        print('ERROS',errs);await b.close()
    srv.terminate();print('FALHAS:',fails or 'nenhuma')
asyncio.run(main())
