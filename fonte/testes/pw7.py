import asyncio, subprocess, time, sys
from playwright.async_api import async_playwright
fails=[]
def ck(n,ok,x=''):
    print(('OK   ' if ok else 'FALHA'),n,x)
    if not ok: fails.append(n)
async def main():
    srv=subprocess.Popen([sys.executable,'-m','http.server','8778','--directory','/home/claude/mesa/site'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1);errs=[]
    async with async_playwright() as p:
        b=await p.chromium.launch()
        pg=await (await b.new_context(viewport={'width':400,'height':800})).new_page()
        pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('http://localhost:8778/index.html');await pg.wait_for_timeout(300)
        url=pg.url
        # menu do canal (compacto) + voltar
        await pg.select_option('#viewSel','compacto')
        await pg.click('button[aria-label="Canal 1, ajustes e efeitos"]');await pg.wait_for_timeout(150)
        await pg.click('#menuBody button[aria-label="Canal 1, FX, efeitos e presets"]');await pg.wait_for_timeout(150)
        await pg.click('details.fx:has(summary[aria-label="Canal 1, equalizador"]) summary')
        await pg.go_back();await pg.wait_for_timeout(200)
        ck('voltar fecha só a tela de Efeitos',not await pg.is_visible('#fxLayer') and await pg.is_visible('#menuLayer'))
        await pg.go_back();await pg.wait_for_timeout(200)
        ck('voltar fecha só o menu',not await pg.is_visible('#menuLayer') and pg.url==url)
        ck('foco volta ao botão',await pg.evaluate("document.activeElement.getAttribute('aria-label')")=='Canal 1, ajustes e efeitos')
        # abrir e fechar por botão; depois voltar não deve quebrar
        await pg.click('button[aria-label="Canal 1, ajustes e efeitos"]');await pg.click('#menuClose');await pg.wait_for_timeout(250)
        ck('Fechar também funciona',not await pg.is_visible('#menuLayer') and pg.url==url)
        await pg.click('#btnHelp');await pg.wait_for_timeout(100);await pg.go_back();await pg.wait_for_timeout(200)
        ck('voltar fecha instruções',not await pg.is_visible('#helpLayer') and pg.url==url)
        await pg.click('#btnProj');await pg.wait_for_timeout(100);await pg.go_back();await pg.wait_for_timeout(200)
        ck('voltar fecha projetos',not await pg.is_visible('#projLayer') and pg.url==url)
        # faixas: painel + voltar
        await pg.select_option('#viewSel','faixas')
        await pg.click('button[aria-label="Canal 1, volume"]');await pg.wait_for_timeout(100)
        ck('painel volume aberto',await pg.is_visible('#vc0'))
        await pg.go_back();await pg.wait_for_timeout(200)
        ck('voltar fecha o painel',not await pg.is_visible('#vc0') and pg.url==url)
        # fechar painel pelo botão e abrir dialogo: sequência
        await pg.click('button[aria-label="Canal 1, volume"]');await pg.click('button[aria-label="Canal 1, volume"]');await pg.wait_for_timeout(250)
        await pg.click('button[aria-label="Canal 1, mais ajustes: copiar efeitos, restaurar"]');await pg.wait_for_timeout(100)
        await pg.go_back();await pg.wait_for_timeout(200)
        ck('voltar depois de painel fechado fecha o menu',not await pg.is_visible('#menuLayer') and pg.url==url)
        # presets dentro do FX
        await pg.click('button[aria-label="Canal 1, FX, efeitos e presets"]');await pg.wait_for_timeout(200)
        ck('lista de presets aparece no FX',await pg.is_visible('#prc0'))
        await pg.select_option('#prc0','vozeco');await pg.wait_for_timeout(100)
        ck('preset com eco liga delay',await pg.get_attribute('#doc0','aria-pressed')=='true' and await pg.input_value('#pgc0')=='3',await pg.evaluate("document.getElementById('avisos').textContent"))
        await pg.select_option('#prc0','limpo')
        ck('limpo desliga',await pg.get_attribute('#doc0','aria-pressed')=='false')
        await pg.click('#fxClose');await pg.wait_for_timeout(150)
        # Gravar duplicado
        vis=await pg.evaluate("[...document.querySelectorAll('button')].filter(b=>/^Gravar/.test(b.textContent)&&b.offsetParent!==null).map(b=>b.id)")
        ck('só um botão Gravar visível',vis==['btnRec'],str(vis))
        # NVDA: todos tabbable
        ti=await pg.evaluate("[...document.querySelectorAll('#grid .card:first-child .tbar button')].map(b=>b.tabIndex)")
        ck('botões da faixa alcançáveis por Tab',all(t==0 for t in ti),str(ti))
        print('ERROS',errs);await b.close()
    srv.terminate();print('FALHAS:',fails or 'nenhuma')
asyncio.run(main())
