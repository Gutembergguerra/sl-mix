import asyncio, subprocess, time, sys
from playwright.async_api import async_playwright
fails=[]
def ck(n,ok,x=''):
    print(('OK   ' if ok else 'FALHA'),n,x)
    if not ok: fails.append(n)
async def main():
    srv=subprocess.Popen([sys.executable,'-m','http.server','8783','--directory','/home/claude/mesa/site'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1);errs=[]
    async with async_playwright() as p:
        b=await p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required'])
        for name,vp in (('retrato',{'width':400,'height':800}),('deitado',{'width':800,'height':360}),('desktop',{'width':1200,'height':800})):
            print('==',name)
            c=await b.new_context(viewport=vp);pg=await c.new_page()
            pg.on('pageerror',lambda e:errs.append(str(e)))
            async def say():
                await pg.wait_for_timeout(150);return await pg.evaluate("document.getElementById('avisos').textContent")
            async def open_rack(k):
                await pg.evaluate("(k)=>{const sec=document.querySelector('[data-ch=\"'+k+'\"]');sec.scrollIntoView();const b=Array.from(sec.querySelectorAll('button')).find(x=>x.offsetParent!==null&&/, FX, efeitos e presets$/.test(x.getAttribute('aria-label')||''));if(!b)throw new Error('sem botão Efeitos');b.click()}",k)
                await pg.wait_for_timeout(250)
            async def open_det(label):
                await pg.click('#fxBody > details.fx:has(summary[aria-label$="%s"]) > summary'%label);await pg.wait_for_timeout(120)
            await pg.goto('http://localhost:8783/index.html');await pg.wait_for_timeout(300)
            for _ in range(2): await pg.click('#btnAddCh')
            goo=await pg.evaluate("Array.from(document.getElementById('goSel').options).map(o=>o.text).join('|')")
            ck('seções soltas saíram da lista Ir para','Reverb de voz' not in goo and 'Afinação de voz' not in goo,goo)
            ck('seções soltas não existem na tela',await pg.evaluate("!document.getElementById('vrSec')&&!document.getElementById('tuSec')"))
            # rack do canal 1
            await open_rack(0)
            ck('tela Efeitos abre',await pg.is_visible('#fxLayer'))
            ck('foco no título','FX, Canal 1'==await pg.inner_text('#fxTitle') and await pg.evaluate("document.activeElement.id")=='fxTitle',await pg.inner_text('#fxTitle'))
            sums=await pg.evaluate("[...document.querySelectorAll('#fxBody > details.fx > summary')].map(b=>b.textContent)")
            ck('lista com os 6 efeitos',sums==['Pré-amplificador','Equalizador','Delay','Chorus','Reverb de voz','Afinação de voz'],str(sums))
            ck('presets dentro do FX, no começo',await pg.evaluate("document.getElementById('fxBody').firstElementChild.contains(document.getElementById('prc0'))"))
            ck('presets saíram do menu Mais',not await pg.evaluate("!!document.querySelector('.xtra select[id^=\"pr\"]:not([id^=\"prc\"])')") and await pg.evaluate("!document.querySelector('.xtra #prc0')"))
            await pg.select_option('#prc0','violao');await pg.wait_for_timeout(200)
            t=await say();ck('preset aplicado fala o canal e o preset','Canal 1: preset aplicado' in t and 'Violão' in t,t)
            ck('preset mexeu no equalizador',await pg.input_value('#elc0')!='0' or await pg.input_value('#ehc0')!='0',await pg.input_value('#ehc0'))
            ck('todos fechados',await pg.evaluate("[...document.querySelectorAll('#fxBody > details.fx')].every(d=>!d.open)"))
            ck('barra Faixas sem botão Presets',await pg.evaluate("!Array.from(document.querySelectorAll('.tbar button')).some(b=>b.textContent==='Presets')"))
            ck('principal inerte',await pg.evaluate("document.getElementById('main').inert"))
            # reverb: envio do canal 1
            await open_det('reverb de voz, desligado')
            ck('envio ao reverb visível',await pg.is_visible('#vsc0'))
            ck('ajustes gerais do reverb dentro do canal',await pg.evaluate("document.getElementById('fxBody').contains(document.getElementById('vrShared'))"))
            await pg.focus('#vsc0')
            for _ in range(4): await pg.keyboard.press('ArrowRight')
            ck('envio 20 por cento',(await pg.get_attribute('#vsc0','aria-valuetext'))=='20 por cento',await pg.get_attribute('#vsc0','aria-valuetext'))
            ck('resumo fala o envio',(await pg.evaluate("document.querySelector('#fxBody > details.fx:nth-child(6) > summary').getAttribute('aria-label')"))=='Canal 1, reverb de voz, envio 20 por cento')
            # afinação
            await open_det('afinação de voz')
            ck('botão Afinar a voz visível',await pg.is_visible('#fxBody button:text-is("Afinar a voz")'))
            ck('canal da afinação é o 1',await pg.input_value('#tuCh')=='0')
            await pg.keyboard.press('Escape');await pg.wait_for_timeout(200)
            ck('Esc fecha só a tela',not await pg.is_visible('#fxLayer'))
            ck('ajustes voltam à reserva',await pg.evaluate("document.getElementById('fxStash').contains(document.getElementById('vrShared'))&&document.getElementById('fxStash').contains(document.getElementById('tuShared'))"))
            ck('detalhes voltaram ao canal',await pg.evaluate("document.querySelector('[data-ch=\"0\"]').contains(document.getElementById('elc0'))"))
            # canal 2 independente
            await open_rack(1)
            ck('tela Efeitos do canal 2','FX, Canal 2'==await pg.inner_text('#fxTitle'),await pg.inner_text('#fxTitle'))
            await open_det('reverb de voz, desligado')
            await pg.focus('#vsc1')
            for _ in range(8): await pg.keyboard.press('ArrowRight')
            ck('canal 2 com 40',await pg.input_value('#vsc1')=='40')
            ck('canal 1 continua com 20',await pg.input_value('#vsc0')=='20')
            await open_det('afinação de voz')
            ck('canal da afinação agora é o 2',await pg.input_value('#tuCh')=='1')
            await pg.click('#fxClose');await pg.wait_for_timeout(200)
            ck('foco volta ao botão Efeitos',(await pg.evaluate("document.activeElement.getAttribute('aria-label')")).endswith('efeitos e presets'),await pg.evaluate("document.activeElement.getAttribute('aria-label')"))
            # nome do canal acompanha o rack
            await pg.evaluate("(k)=>{const sec=document.querySelector('[data-ch=\"0\"]');Array.from(sec.querySelectorAll('button')).find(x=>x.offsetParent!==null&&/(ajustes e efeitos|mais ajustes)/.test(x.getAttribute('aria-label')||'')).click()}",0)
            await pg.wait_for_timeout(250)
            await pg.fill('#nmc0','Violão');await pg.press('#nmc0','Tab');await pg.wait_for_timeout(200)
            await pg.click('#menuBody button[aria-label="Violão, FX, efeitos e presets"]');await pg.wait_for_timeout(200)
            ck('título do rack com o nome','FX, Violão'==await pg.inner_text('#fxTitle'),await pg.inner_text('#fxTitle'))
            ck('resumo do reverb com o nome',(await pg.evaluate("document.querySelector('#fxBody > details.fx:nth-child(6) > summary').getAttribute('aria-label')"))=='Violão, reverb de voz, envio 20 por cento')
            await pg.go_back();await pg.wait_for_timeout(250)
            ck('voltar fecha só a tela de Efeitos',not await pg.is_visible('#fxLayer') and await pg.is_visible('#menuLayer'))
            await pg.click('#menuClose');await pg.wait_for_timeout(200)
            # projeto guarda os envios
            await pg.click('#btnProj');await pg.wait_for_timeout(200);await pg.click('#btnDemo');await pg.wait_for_timeout(900)
            await pg.fill('#pjName','rack');await pg.click('text=Salvar projeto no aparelho');await pg.wait_for_timeout(500)
            await pg.click('button:text-is("Novo projeto")');await pg.wait_for_timeout(600)
            await pg.click('#btnProj');await pg.wait_for_timeout(300)
            await pg.click('button:text-is("Abrir projeto selecionado")');await pg.wait_for_timeout(900)
            await pg.click('#projClose');await pg.wait_for_timeout(200)
            ck('projeto guardou os envios',(await pg.input_value('#vsc0'),await pg.input_value('#vsc1'))==('20','40'),str((await pg.input_value('#vsc0'),await pg.input_value('#vsc1'))))
            # tocar com reverb ligado não pode dar erro
            await pg.evaluate("document.getElementById('btnPlay').click()");await pg.wait_for_timeout(1200)
            await pg.evaluate("document.getElementById('btnPlay').click()");await pg.wait_for_timeout(200)
            # remover canal zera o envio
            await pg.click('#btnRmCh');await pg.click('#btnRmCh');await pg.wait_for_timeout(250)
            ck('remover canal zera o envio dele',await pg.evaluate("document.getElementById('vsc'+(document.querySelectorAll('[data-ch]:not([hidden])').length)).value")=='0')
            ck('sem rolagem lateral',await pg.evaluate("document.documentElement.scrollWidth<=document.documentElement.clientWidth+1"))
            await c.close()
        await b.close()
    srv.terminate()
    print('ERROS JS:',errs or 'nenhum');print('FALHAS:',fails or 'nenhuma')
asyncio.run(main())
