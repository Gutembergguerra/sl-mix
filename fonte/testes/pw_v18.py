import asyncio, subprocess, time, sys
from playwright.async_api import async_playwright
fails=[]
def ck(n,ok,x=''):
    print(('OK   ' if ok else 'FALHA'),n,x)
    if not ok: fails.append(n)
async def main():
    srv=subprocess.Popen([sys.executable,'-m','http.server','8788','--directory','/home/claude/mesa/site'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1);errs=[]
    async with async_playwright() as p:
        b=await p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required'])
        for name,vp in (('retrato',{'width':400,'height':800}),('deitado',{'width':800,'height':360}),('desktop',{'width':1200,'height':800})):
            print('==',name)
            c=await b.new_context(viewport=vp);pg=await c.new_page()
            pg.on('pageerror',lambda e:errs.append(str(e)))
            say=lambda: pg.evaluate("document.getElementById('avisos').textContent")
            async def rename(k,nm):
                await pg.evaluate("(k)=>{const sec=document.querySelector('[data-ch=\"'+k+'\"]');sec.scrollIntoView();Array.from(sec.querySelectorAll('button')).find(x=>x.offsetParent!==null&&/(ajustes e efeitos|mais ajustes)/.test(x.getAttribute('aria-label')||'')).click()}",k)
                await pg.wait_for_timeout(250);await pg.fill('#nmc%d'%k,nm);await pg.press('#nmc%d'%k,'Tab');await pg.wait_for_timeout(150)
                await pg.click('#menuClose');await pg.wait_for_timeout(200)
            await pg.goto('http://localhost:8788/index.html');await pg.wait_for_timeout(300)
            for _ in range(3): await pg.click('#btnAddCh')
            await pg.click('#btnProj');await pg.wait_for_timeout(200);await pg.click('#btnDemo');await pg.wait_for_timeout(900);await pg.click('#projClose')
            # esvazia canais além dos 3 (demo carrega 6 e depois reduz)
            for _ in range(3):
                await pg.click('#btnRmCh');await pg.wait_for_timeout(200)
                await pg.click('#rmBody button:text-is("Remover")');await pg.click('#rmBody button:text-is("Remover")');await pg.wait_for_timeout(250)
            ck('ficaram 3 canais',await pg.evaluate("document.querySelectorAll('[data-ch]:not([hidden])').length")==3)
            await rename(0,'Violão');await rename(1,'Voz');await rename(2,'Bateria')
            # edita o canal 3 (cortar) e mexe em volume/efeito/reverb
            await pg.evaluate("(()=>{const sec=document.querySelector('[data-ch=\"2\"]');Array.from(sec.querySelectorAll('button')).find(x=>x.offsetParent!==null&&/editar áudio$/.test(x.getAttribute('aria-label')||'')).click()})()");await pg.wait_for_timeout(250)
            await pg.fill('#edA','1');await pg.press('#edA','Tab');await pg.fill('#edB','2');await pg.press('#edB','Tab')
            await pg.click('button:text-is("Cortar")');await pg.wait_for_timeout(200)
            dur3=await pg.evaluate("chansDur?0:0") if False else None
            ed3=await pg.inner_text('#fpc2') if await pg.locator('#fpc2').count() else ''
            await pg.keyboard.press('Escape');await pg.wait_for_timeout(200)
            fileEl3=await pg.inner_text('#fc2')
            await pg.evaluate("document.getElementById('vc2').value=-12;document.getElementById('vc2').dispatchEvent(new Event('input',{bubbles:true}))")
            await pg.evaluate("document.getElementById('elc2').value=5;document.getElementById('elc2').dispatchEvent(new Event('input',{bubbles:true}))")
            await pg.evaluate("document.getElementById('vsc2').value=35;document.getElementById('vsc2').dispatchEvent(new Event('input',{bubbles:true}))")
            await pg.evaluate("document.getElementById('muc2').click()")
            antes={'vol':await pg.input_value('#vc2'),'eq':await pg.input_value('#elc2'),'vs':await pg.input_value('#vsc2'),'mudo':await pg.get_attribute('#muc2','aria-pressed')}
            ck('canal 3 editado (marcado como editado)','editado' in fileEl3,fileEl3)
            # Remover canal pergunta qual (canal do meio = Voz)
            await pg.click('#btnRmCh');await pg.wait_for_timeout(250)
            ck('pergunta qual canal',await pg.is_visible('#rmLayer') and await pg.evaluate("document.activeElement.id")=='rmTitle')
            opts=await pg.evaluate("[...document.getElementById('rmSel').options].map(o=>o.text)")
            ck('lista mostra nomes e se tem áudio',len(opts)==3 and opts[0].startswith('Violão, com áudio') and opts[1].startswith('Voz') and opts[2].startswith('Bateria'),str(opts))
            ck('vem escolhido o último',await pg.input_value('#rmSel')=='2')
            # Cancelar
            await pg.click('#rmBody button:text-is("Cancelar")');await pg.wait_for_timeout(250)
            ck('Cancelar fecha sem remover',not await pg.is_visible('#rmLayer') and await pg.evaluate("document.querySelectorAll('[data-ch]:not([hidden])').length")==3)
            # remove a Voz (meio)
            await pg.click('#btnRmCh');await pg.wait_for_timeout(250)
            await pg.select_option('#rmSel','1')
            await pg.click('#rmBody button:text-is("Remover")');await pg.wait_for_timeout(200);t=await say()
            ck('com áudio pede para apertar de novo','Voz tem áudio' in t,t)
            ck('tela continua aberta',await pg.is_visible('#rmLayer'))
            await pg.click('#rmBody button:text-is("Remover")');await pg.wait_for_timeout(400);t=await say()
            ck('removeu a Voz e diz que os de baixo subiram','Voz removido' in t and 'subiram' in t and '2 canais' in t,t)
            ck('tela fechou',not await pg.is_visible('#rmLayer'))
            ck('mesa tem 2 canais',await pg.evaluate("document.querySelectorAll('[data-ch]:not([hidden])').length")==2)
            nomes=await pg.evaluate("Array.from(document.querySelectorAll('[data-ch]:not([hidden]) h3')).map(h=>h.textContent.replace(/^\\d/,'')).join('|')")
            ck('o canal Bateria subiu para o lugar 2',nomes.endswith('Bateria') and 'Voz' not in nomes,nomes)
            depois={'vol':await pg.input_value('#vc1'),'eq':await pg.input_value('#elc1'),'vs':await pg.input_value('#vsc1'),'mudo':await pg.get_attribute('#muc1','aria-pressed')}
            ck('volume, equalizador, reverb e mudo ficaram iguais',depois==antes,str(antes)+' -> '+str(depois))
            ck('canal vazio no fim voltou ao padrão',await pg.input_value('#vc2')=='0' and await pg.input_value('#vsc2')=='0' and await pg.get_attribute('#muc2','aria-pressed')=='false')
            fileEl=await pg.inner_text('#fc1')
            ck('áudio editado subiu junto',fileEl==fileEl3 and 'editado' in fileEl,fileEl)
            # desfazer o corte continua funcionando no canal que subiu
            await pg.evaluate("(()=>{const sec=document.querySelector('[data-ch=\"1\"]');Array.from(sec.querySelectorAll('button')).find(x=>x.offsetParent!==null&&/editar áudio$/.test(x.getAttribute('aria-label')||'')).click()})()");await pg.wait_for_timeout(250)
            await pg.click('button:text-is("Desfazer")');await pg.wait_for_timeout(200);t=await say()
            ck('Desfazer do canal que subiu devolve o trecho','Desfeito' in t and 'Bateria' in t,t)
            await pg.keyboard.press('Escape');await pg.wait_for_timeout(200)
            # remover o último com um canal só: direto
            await pg.click('#btnRmCh');await pg.wait_for_timeout(250)
            await pg.select_option('#rmSel','0');await pg.click('#rmBody button:text-is("Remover")');await pg.click('#rmBody button:text-is("Remover")');await pg.wait_for_timeout(300)
            ck('sobrou 1 canal',await pg.evaluate("document.querySelectorAll('[data-ch]:not([hidden])').length")==1)
            ck('rótulo com 1 canal diz qual remove',(await pg.get_attribute('#btnRmCh','aria-label')).startswith('Remover canal. Remove o'),await pg.get_attribute('#btnRmCh','aria-label'))
            # Esc cancela a pergunta
            await pg.click('#btnAddCh');await pg.wait_for_timeout(150);await pg.click('#btnRmCh');await pg.wait_for_timeout(250)
            ck('com 2 canais pergunta de novo',await pg.is_visible('#rmLayer'))
            await pg.keyboard.press('Escape');await pg.wait_for_timeout(250)
            ck('Esc cancela',not await pg.is_visible('#rmLayer'))
            ck('sem rolagem lateral',await pg.evaluate("document.documentElement.scrollWidth<=document.documentElement.clientWidth+1"))
            await c.close()
        await b.close()
    srv.terminate()
    print('ERROS JS:',errs or 'nenhum');print('FALHAS:',fails or 'nenhuma')
asyncio.run(main())
