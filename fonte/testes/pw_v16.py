import asyncio, subprocess, time, sys
from playwright.async_api import async_playwright
fails=[]
def ck(n,ok,x=''):
    print(('OK   ' if ok else 'FALHA'),n,x)
    if not ok: fails.append(n)
async def main():
    srv=subprocess.Popen([sys.executable,'-m','http.server','8785','--directory','/home/claude/mesa/site'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1);errs=[]
    async with async_playwright() as p:
        b=await p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required'])
        for name,vp in (('retrato',{'width':400,'height':800}),('deitado',{'width':800,'height':360}),('desktop',{'width':1200,'height':800})):
            print('==',name)
            c=await b.new_context(viewport=vp);pg=await c.new_page()
            pg.on('pageerror',lambda e:errs.append(str(e)))
            async def say():
                await pg.wait_for_timeout(150);return await pg.evaluate("document.getElementById('avisos').textContent")
            await pg.goto('http://localhost:8785/index.html');await pg.wait_for_timeout(300)
            ck('lista Ir para sem título visível',await pg.evaluate("!document.querySelector('label[for=goSel]')")and(await pg.get_attribute('#goSel','aria-label'))=='Ir para')
            for _ in range(2): await pg.click('#btnAddCh')
            await pg.click('#btnProj');await pg.wait_for_timeout(200);await pg.click('#btnDemo');await pg.wait_for_timeout(900);await pg.click('#projClose')
            await pg.evaluate("(()=>{const sec=document.querySelector('[data-ch=\"0\"]');Array.from(sec.querySelectorAll('button')).find(x=>x.offsetParent!==null&&/editar áudio$/.test(x.getAttribute('aria-label')||'')).click()})()");await pg.wait_for_timeout(250)
            ck('tela Editar áudio abre',await pg.is_visible('#edLayer'))
            # topo: Tocar, Parar, Concluir, nessa ordem, à vista
            top=await pg.evaluate("[...document.querySelectorAll('#edLayer .menu-head button')].map(b=>b.id)")
            ck('topo tem Tocar, Parar e Concluir',top==['edPlay','edStop','edClose'],str(top))
            # nenhum grupo fechado na tela
            ck('sem grupos fechados na tela',await pg.evaluate("document.querySelectorAll('#edBody details').length")==0)
            # ordem dos botões principais
            ordem=await pg.evaluate("[...document.querySelectorAll('#edBody button')].slice(0,8).map(b=>b.textContent)")
            ck('ordem: marcar, voltar/avançar',ordem[:4]==['Marcar início aqui','Marcar fim aqui','Voltar','Avançar'],str(ordem))
            ck('barra Posição logo abaixo do Canal',await pg.evaluate("(()=>{const l=[...document.querySelectorAll('#edBody select,#edBody input,#edBody button')];return l[0].id==='edCh'&&l[1].id==='edPos'})()"))
            # fluxo do usuário
            await pg.click('#edPlay');await pg.wait_for_timeout(1500)
            ck('Tocar vira Pausar',(await pg.inner_text('#edPlay'))=='Pausar',await pg.inner_text('#edPlay'))
            await pg.click('#edPlay');await pg.wait_for_timeout(200)
            t=await say();ck('barra Posição fala o tempo ao pausar','segundo' in (await pg.get_attribute('#edPos','aria-valuetext')) and 'no total' in (await pg.get_attribute('#edPos','aria-valuetext')),await pg.get_attribute('#edPos','aria-valuetext'))
            ck('pausou e falou o ponto','Pausado em' in t,t)
            await pg.click('text=Marcar início aqui');t=await say();ck('marcou início','Início marcado em' in t,t)
            iniA=await pg.input_value('#edA')
            await pg.click('#edPlay');await pg.wait_for_timeout(1500);await pg.click('#edPlay');await pg.wait_for_timeout(200)
            await pg.click('text=Marcar fim aqui');t=await say();ck('marcou fim com duração','Fim marcado em' in t and 'Duração' in t,t)
            ck('campos Início e Fim preenchidos',bool(iniA) and bool(await pg.input_value('#edB')),iniA+' / '+await pg.input_value('#edB'))
            # voltar e avançar mexem o cursor pelo passo
            # Tocar começa sempre no início marcado
            await pg.click('#edPlay');await pg.wait_for_timeout(300);t=await say()
            ck('Tocar começa no início marcado','a partir do início marcado' in t,t)
            await pg.wait_for_timeout(800);await pg.click('#edPlay');await pg.wait_for_timeout(200)
            await pg.click('#edPlay');await pg.wait_for_timeout(300);t=await say()
            ck('Tocar de novo volta ao início marcado','a partir do início marcado' in t,t)
            await pg.click('#edPlay');await pg.wait_for_timeout(200)
            # Voltar e Avançar dizem direção e tempo do passo
            await pg.select_option('#edStep','1')
            await pg.click('#edBody button[aria-label="Avançar um passo"]');t=await say();ck('Avançar diz quanto','Avançou 1 segundo. Posição:' in t,t)
            await pg.click('#edBody button[aria-label="Voltar um passo"]');t=await say();ck('Voltar diz quanto','Voltou 1 segundo. Posição:' in t,t)
            await pg.select_option('#edStep','0.1')
            await pg.click('#edBody button[aria-label="Avançar um passo"]');t=await say();ck('passo de 100 ms','Avançou 100 milissegundos' in t,t)
            await pg.select_option('#edStep','0.01')
            await pg.click('#edBody button[aria-label="Voltar um passo"]');t=await say();ck('passo de 10 ms','Voltou 10 milissegundos' in t,t)
            await pg.click('text=Início: avançar');t=await say();ck('Início avança com mensagem clara','Início avançou 10 milissegundos, agora em' in t,t)
            await pg.click('text=Fim: voltar');t=await say();ck('Fim volta com mensagem clara','Fim voltou 10 milissegundos, agora em' in t,t)
            # parado no começo: Voltar avisa
            await pg.click('#edStop');await pg.wait_for_timeout(200)
            await pg.click('#edBody button[aria-label="Voltar um passo"]');t=await say();ck('no início, Voltar avisa','Já está no início' in t,t)
            await pg.click('text=Ouvir trecho');t=await say();ck('Ouvir trecho','Tocando o trecho' in t,t)
            await pg.click('#edPlay');await pg.wait_for_timeout(100)
            await pg.click('button:text-is("Cortar")');t=await say();ck('Cortou','Corte feito' in t,t)
            await pg.click('button:text-is("Desfazer")');t=await say();ck('Desfez','Desfeito' in t,t)
            # Parar volta ao início
            await pg.click('#edPlay');await pg.wait_for_timeout(1000)
            await pg.click('#edStop');t=await say();ck('Parar volta ao início','Parado' in t and 'início' in t,t)
            ck('Tocar de volta no botão após Parar',(await pg.inner_text('#edPlay'))=='Tocar')
            ck('Separar em faixas à vista',await pg.evaluate("[...document.querySelectorAll('#edBody button')].some(b=>b.textContent==='Marcar divisão aqui'&&b.offsetParent!==null)"))
            ck('sem rolagem lateral',await pg.evaluate("document.documentElement.scrollWidth<=document.documentElement.clientWidth+1"))
            await pg.keyboard.press('Escape');await pg.wait_for_timeout(200)
            ck('Esc fecha só a tela',not await pg.is_visible('#edLayer'))
            await c.close()
        await b.close()
    srv.terminate()
    print('ERROS JS:',errs or 'nenhum');print('FALHAS:',fails or 'nenhuma')
asyncio.run(main())
