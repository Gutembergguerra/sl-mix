import asyncio, subprocess, time, sys
from playwright.async_api import async_playwright
fails=[]
def ck(n,ok,x=''):
    print(('OK   ' if ok else 'FALHA'),n,x)
    if not ok: fails.append(n)
async def main():
    srv=subprocess.Popen([sys.executable,'-m','http.server','8781','--directory','/home/claude/mesa/site'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1);errs=[]
    async with async_playwright() as p:
        b=await p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required'])
        for name,vp in (('retrato',{'width':400,'height':800}),('deitado',{'width':800,'height':360}),('desktop',{'width':1200,'height':800})):
            print('==',name)
            c=await b.new_context(viewport=vp,accept_downloads=True);pg=await c.new_page()
            pg.on('pageerror',lambda e:errs.append(str(e)))
            async def say():
                await pg.wait_for_timeout(150);return await pg.evaluate("document.getElementById('avisos').textContent")
            async def open_menu(k):
                await pg.evaluate("(k)=>{const c=document.querySelector('[data-ch=\"'+k+'\"]');c.scrollIntoView()}",k)
                await pg.evaluate("(k)=>{const sec=document.querySelector('[data-ch=\"'+k+'\"]');const b=Array.from(sec.querySelectorAll('button')).find(x=>x.offsetParent!==null&&/(ajustes e efeitos|mais ajustes)/.test(x.getAttribute('aria-label')||''));if(!b)throw new Error('sem botão de menu');b.click()}",k)
                await pg.wait_for_timeout(250)
            async def rename(k,nm):
                await open_menu(k)
                f=pg.locator('#nmc%d'%k)
                await f.fill(nm);await f.press('Tab');await pg.wait_for_timeout(200)
            await pg.goto('http://localhost:8781/index.html');await pg.wait_for_timeout(300)
            for _ in range(2): await pg.click('#btnAddCh')
            # campo de nome
            await open_menu(0)
            ck('campo Nome do canal visível no menu',await pg.is_visible('#nmc0'))
            al=await pg.get_attribute('#nmc0','aria-label');ck('campo falado uma vez (aria-label + rótulo escondido)',al.startswith('Canal 1, nome do canal') and await pg.evaluate("document.querySelector('label[for=nmc0]').getAttribute('aria-hidden')")=='true',al)
            await pg.keyboard.press('Escape');await pg.wait_for_timeout(200)
            ck('campo some quando o menu fecha',not await pg.is_visible('#nmc0'))
            # renomear
            await rename(0,'Violão')
            t=await say();ck('fala nome definido','Violão' in t and 'definido' in t,t)
            ck('título do menu',(await pg.inner_text('#menuTitle')).startswith('Violão, ajustes'),await pg.inner_text('#menuTitle'))
            ck('aria-label do campo trocou',(await pg.get_attribute('#nmc0','aria-label')).startswith('Violão, nome do canal'))
            await pg.click('#menuClose');await pg.wait_for_timeout(200)
            ck('título do canal 1','Violão' in await pg.inner_text('[data-ch="0"] h3'),await pg.inner_text('[data-ch="0"] h3'))
            n_old=await pg.evaluate("Array.from(document.querySelectorAll('[data-ch=\"0\"] [aria-label]')).filter(e=>(e.getAttribute('aria-label')||'').startsWith('Canal 1')).length")
            ck('nenhum botão do canal 1 ficou com nome antigo',n_old==0,str(n_old))
            ck('lista do canal para gravar',await pg.evaluate("Array.from(document.getElementById('recCh').options).map(o=>o.text).join('|')")=='Violão|Canal 2',await pg.evaluate("Array.from(document.getElementById('recCh').options).map(o=>o.text).join('|')"))
            ck('botão Gravar usa o nome',await pg.evaluate("document.querySelector('#recSec .btn.primary').textContent")=='Gravar em Violão',await pg.evaluate("document.querySelector('#recSec .btn.primary').textContent"))
            # segundo canal
            await rename(1,'Voz');t=await say();ck('canal 2 renomeado','Voz' in t,t)
            await pg.click('#menuClose');await pg.wait_for_timeout(200)
            ck('Ir para tem os nomes',await pg.evaluate("Array.from(document.getElementById('goSel').options).filter(o=>/^c\\d$/.test(o.value)).map(o=>o.text).join('|')")=='Violão|Voz')
            # mudo fala o nome
            mu=await pg.evaluate("(()=>{const b=document.getElementById('muc0');return b.getAttribute('aria-label')})()")
            ck('botão Mudo com nome',mu=='Violão, mudo',mu)
            await pg.evaluate("document.getElementById('muc0').click()");t=await say();ck('Mudo fala o nome',t.startswith('Violão mudo'),t)
            await pg.evaluate("document.getElementById('muc0').click()")
            # slider fala nome
            await pg.evaluate("document.querySelector('[aria-label=\"Voz, volume, aumentar\"]').click()");t=await say();ck('volume fala o nome',t.startswith('Voz, volume'),t)
            # edição usa o nome
            await pg.evaluate("(()=>{const b=Array.from(document.querySelectorAll('button')).find(x=>x.offsetParent!==null&&x.getAttribute('aria-label')==='Voz, editar áudio');b.click()})()");await pg.wait_for_timeout(250)
            ck('Editar áudio com nome',(await pg.inner_text('#edTitle')).startswith('Editar áudio, Voz'),await pg.inner_text('#edTitle'))
            await pg.keyboard.press('Escape');await pg.wait_for_timeout(200)
            # projeto: salvar, novo, abrir
            await pg.click('#btnProj');await pg.wait_for_timeout(200)
            await pg.click('#btnDemo');await pg.wait_for_timeout(900)
            await pg.fill('#pjName','teste nomes');await pg.click('text=Salvar projeto no aparelho');await pg.wait_for_timeout(500)
            await pg.click('text=Novo projeto >> nth=-1') if False else await pg.click('button:text-is("Novo projeto")');await pg.wait_for_timeout(600)
            ck('novo projeto sem canais',await pg.evaluate("document.querySelectorAll('[data-ch]:not([hidden])').length")==0)
            await pg.click('#btnProj');await pg.wait_for_timeout(300)
            await pg.click('button:text-is("Abrir projeto selecionado")');await pg.wait_for_timeout(800)
            await pg.click('#projClose');await pg.wait_for_timeout(200)
            nomes=await pg.evaluate("Array.from(document.querySelectorAll('[data-ch]:not([hidden]) h3')).map(h=>h.textContent).join('|')")
            ck('projeto guardou os nomes','Violão' in nomes and 'Voz' in nomes,nomes)
            # apagar nome volta ao padrão
            await rename(0,'');t=await say();ck('nome removido volta a Canal 1','Canal 1' in t,t)
            await pg.click('#menuClose');await pg.wait_for_timeout(200)
            ck('título voltou','Canal 1' in await pg.inner_text('[data-ch="0"] h3'))
            # remover canal: fala o nome que o canal tinha, e o canal novo volta ao padrão
            n=await pg.evaluate("document.querySelectorAll('[data-ch]:not([hidden])').length")
            ult=await pg.evaluate("(()=>{const l=Array.from(document.querySelectorAll('[data-ch]:not([hidden])'));return l[l.length-1].getAttribute('data-ch')})()")
            await rename(int(ult),'Bateria');await pg.click('#menuClose');await pg.wait_for_timeout(200)
            await pg.click('#btnRmCh');await pg.wait_for_timeout(250)
            ck('Remover canal pergunta qual',await pg.is_visible('#rmLayer'))
            await pg.click('#rmBody button:text-is("Remover")');await pg.wait_for_timeout(150);t0=await say();ck('remover com áudio pede confirmação','Bateria tem áudio' in t0,t0)
            await pg.click('#rmBody button:text-is("Remover")');await pg.wait_for_timeout(250);t=await say();ck('remover fala o nome','Bateria removido' in t,t)
            await pg.click('#btnAddCh');await pg.wait_for_timeout(250)
            lab2=await pg.get_attribute('#muc'+ult,'aria-label')
            ck('canal novo volta com nome padrão',lab2=='Canal %d, mudo'%(int(ult)+1),lab2)
            ck('sem rolagem lateral',await pg.evaluate("document.documentElement.scrollWidth<=document.documentElement.clientWidth+1"))
            await c.close()
        await b.close()
    srv.terminate()
    print('ERROS JS:',errs or 'nenhum');print('FALHAS:',fails or 'nenhuma')
asyncio.run(main())
