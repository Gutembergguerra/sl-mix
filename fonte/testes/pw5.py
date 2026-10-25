import asyncio, subprocess, time, sys
from playwright.async_api import async_playwright
OUT='/tmp/claude-0/-home-claude/4129777c-0cf8-5d04-a000-871a28639019/scratchpad/smoke/'
fails=[]
def ck(name,ok,extra=''):
    print(('OK   ' if ok else 'FALHA'),name,extra)
    if not ok: fails.append(name)
async def main():
    srv=subprocess.Popen([sys.executable,'-m','http.server','8769','--directory','/home/claude/mesa/site'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    time.sleep(1); errs=[]
    try:
        async with async_playwright() as p:
            b=await p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required'])
            for name,vp in (('retrato',{'width':400,'height':800}),('paisagem',{'width':800,'height':360})):
                print('==',name)
                ctx=await b.new_context(viewport=vp); page=await ctx.new_page()
                page.on('pageerror',lambda e:errs.append('pageerror: '+str(e)))
                page.on('console',lambda m:errs.append('console: '+m.text) if m.type=='error' and 'Failed to load' not in m.text else None)
                await page.add_init_script("localStorage.setItem('mesa-view2','compacto')")
                await page.goto('http://localhost:8769/index.html'); await page.wait_for_timeout(400)
                say=lambda: page.evaluate("document.getElementById('avisos').textContent")
                gy=await page.evaluate("document.getElementById('grid').getBoundingClientRect().top")
                ck('canais aparecem sem rolar muito',gy<(620 if name=='retrato' else 290),f'top={round(gy)}')
                ck('vista inicial compacto',await page.input_value('#viewSel')=='compacto')
                # abre Arquivos pelo Ir para
                await page.select_option('#goSel','files'); await page.wait_for_timeout(150)
                ck('Ir para abre Projetos e arquivos',await page.is_visible('#projLayer'))
                ck('foco no título',await page.evaluate('document.activeElement.id')=='projTitle')
                await page.click('#btnDemo'); await page.wait_for_timeout(600); await page.click('#projClose'); await page.wait_for_timeout(100)
                s0=await page.inner_text('#sm-c0') if False else await page.inner_text('#smc0')
                ck('resumo canal 1',('Sem efeitos' in s0),s0)
                # abre menu
                await page.click('button[aria-label="Canal 1, ajustes e efeitos"]'); await page.wait_for_timeout(200)
                ck('menu visível',await page.is_visible('#menuLayer'))
                ck('principal inerte',await page.evaluate("document.getElementById('main').inert"))
                ck('foco no título do menu',await page.evaluate("document.activeElement.id")=='menuTitle')
                ck('botão Efeitos dentro do menu',await page.evaluate("document.getElementById('menuBody').contains(document.querySelector('#menuBody .rack-btn'))"))
                ck('Gravação sincronizada canal 1',await page.input_value('#recCh')=='0')
                await page.click('#menuBody button[aria-label="Canal 1, FX, efeitos e presets"]'); await page.wait_for_timeout(200)
                ck('EQ dentro da tela de Efeitos',await page.evaluate("document.getElementById('fxBody').contains(document.getElementById('elc0'))"))
                await page.click('details.fx:has(summary[aria-label="Canal 1, equalizador"]) summary')
                await page.focus('#elc0'); await page.keyboard.press('ArrowUp'); await page.keyboard.press('ArrowUp')
                ck('EQ canal 1 mudou',await page.input_value('#elc0')=='2',await page.get_attribute('#elc0','aria-valuetext'))
                await page.click('#fxClose'); await page.wait_for_timeout(150)
                ck('menu continua aberto depois de Concluir',await page.is_visible('#menuLayer') and not await page.is_visible('#fxLayer'))
                ck('EQ canal 2 intacto',await page.input_value('#elc1')=='0')
                # próximo canal
                await page.click('#menuNext'); await page.wait_for_timeout(100)
                ck('próximo canal',(await page.inner_text('#menuTitle')).startswith('Canal 2'))
                ck('EQ canal 1 voltou ao cartão',await page.evaluate("document.getElementById('grid').contains(document.getElementById('elc0'))"))
                await page.click('#menuPrev')
                # bypass, preset, copiar
                await page.click('button[aria-label="Canal 1, ouvir sem efeitos"]')
                ck('bypass ligado',await page.get_attribute('button[aria-label="Canal 1, ouvir sem efeitos"]','aria-pressed')=='true')
                await page.click('#menuBody button[aria-label="Canal 1, FX, efeitos e presets"]'); await page.wait_for_timeout(200)
                await page.select_option('#prc0','voz'); await page.wait_for_timeout(100)
                ck('preset voz',await page.input_value('#pgc0')=='3',await say())
                await page.click('#fxClose'); await page.wait_for_timeout(150)
                await page.select_option('#cpc0','all'); await page.wait_for_timeout(100)
                ck('copiar para todos',await page.input_value('#pgc5')=='3' and await page.input_value('#ehc3')=='3')
                await page.click('button[aria-label="Canal 1, restaurar efeitos"]')
                ck('restaurar pede confirmação',await page.input_value('#pgc0')=='3',await say())
                await page.click('button[aria-label="Canal 1, restaurar efeitos"]')
                ck('restaurar zera',await page.input_value('#pgc0')=='0')
                # play no menu
                await page.click('#menuPlay'); await page.wait_for_timeout(1200)
                ck('tocar no menu muda texto',(await page.inner_text('#menuPlay'))=='Pausar')
                await page.click('#menuPlay'); await page.wait_for_timeout(150)
                # fechar
                await page.keyboard.press('Escape'); await page.wait_for_timeout(150)
                ck('Esc fecha',not await page.is_visible('#menuLayer'))
                ck('foco volta ao botão do canal',await page.evaluate("document.activeElement.getAttribute('aria-label')")=='Canal 1, ajustes e efeitos')
                ck('principal ativo',not await page.evaluate("document.getElementById('main').inert"))
                s0=await page.inner_text('#smc0'); ck('resumo atualiza',('Ouvindo sem efeitos' in s0),s0)
                # duplo clique
                await page.dblclick('#hc2'); await page.wait_for_timeout(150)
                ck('duplo toque abre canal 3',(await page.inner_text('#menuTitle')).startswith('Canal 3'))
                await page.click('#menuClose'); await page.wait_for_timeout(100)
                # seções exclusivas
                await page.select_option('#goSel','rec'); await page.select_option('#goSel','master')
                op=await page.evaluate("[...document.querySelectorAll('.acc-btn')].filter(b=>b.getAttribute('aria-expanded')==='true').length")
                ck('só uma seção aberta',op==1,str(op))
                # todas as vistas sem estouro
                for v in ('lista','lado','um','mesa','compacto'):
                    await page.select_option('#viewSel',v); await page.wait_for_timeout(100)
                    ov=await page.evaluate("document.documentElement.scrollWidth-innerWidth")
                    ck('vista '+v+' sem estouro horizontal',ov<=1,str(ov))
                await page.select_option('#viewSel','compacto')
                if name=='paisagem':
                    r=await page.evaluate("['colL','colC','colR'].map(c=>{const r=document.querySelector('.'+c).getBoundingClientRect();return [Math.round(r.left),Math.round(r.width),Math.round(r.top),Math.round(r.bottom)]})")
                    ck('3 colunas lado a lado',r[0][0]<r[1][0]<r[2][0] and r[1][2]==r[0][2],str(r))
                    ck('página não rola na paisagem',await page.evaluate("document.documentElement.scrollHeight<=innerHeight+1"),str(await page.evaluate("[document.documentElement.scrollHeight,innerHeight]")))
                await page.screenshot(path=OUT+f'v2_{name}.png')
            print('ERROS JS:',errs or 'nenhum')
            await b.close()
    finally: srv.terminate()
    print('FALHAS:',fails or 'nenhuma')
asyncio.run(main())
