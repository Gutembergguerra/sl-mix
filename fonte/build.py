s=open('/home/claude/mesa/app-body.html').read()
i=s.index('<div class="wrap"')
head=s[:i].replace('<meta name="claude:viewport-fit-sides" content="cover">\n','')
body=s[i:]
html=('<!doctype html>\n<html lang="pt-BR">\n<head>\n<meta charset="utf-8">\n'
 '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
 '<meta name="theme-color" content="#0a6b73">\n'
 '<link rel="manifest" href="manifest.webmanifest">\n'
 '<link rel="icon" href="icon-192.png">\n<link rel="apple-touch-icon" href="icon-192.png">\n'
 +head+'</head>\n<body>\n'+body+'</body>\n</html>\n')
open('/home/claude/mesa/site/index.html','w').write(html)
sw=open('/home/claude/mesa/site/sw.js').read()
open('/home/claude/mesa/site/sw.js','w').write(sw)

# ---- cópia de teste (endereço reservado, não divulgado) ----
import os,shutil,re
BETA='teste-7k2m9x'
bd='/home/claude/mesa/site/'+BETA
os.makedirs(bd,exist_ok=True)
bh=html.replace('<title>SL-Mixer: Áudio Acessível</title>','<title>SL-Mixer Teste</title>').replace('<h1>SL-Mixer</h1>','<h1>SL-Mixer Teste</h1>')
open(bd+'/index.html','w').write(bh)
for f in ('icon-192.png','icon-512.png'):
    shutil.copy('/home/claude/mesa/site/'+f,bd+'/'+f)
mf=open('/home/claude/mesa/site/manifest.webmanifest',encoding='utf-8').read()
mf=mf.replace('"name": "SL-Mixer: Áudio Acessível"','"name": "SL-Mixer Teste"').replace('"short_name": "SL-Mixer"','"short_name": "SL-Mixer Teste"')
open(bd+'/manifest.webmanifest','w',encoding='utf-8').write(mf)
sw2=re.sub(r"const CACHE = '[^']*';","const CACHE = 'sl-mix-teste-v17';",sw)
sw2=re.sub(r"\n  if \(url.indexOf\('/teste-'\)[^\n]*",'',sw2)
open(bd+'/sw.js','w').write(sw2)
