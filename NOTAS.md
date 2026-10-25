# SL-Mix: Áudio Acessível. Notas do projeto

Aplicativo web (PWA) de mesa de áudio com 6 canais e Master, feito para funcionar bem com leitor de tela (NVDA no Windows, TalkBack no Android). Autor: Gutenberg Guerra Lima. Todos os direitos reservados.

## Arquivos
- `index.html`: o app inteiro (HTML, CSS e JavaScript num arquivo só).
- `sw.js`: cache para funcionar sem internet. Aumentar o número em `CACHE` a cada publicação.
- `manifest.webmanifest`, `icon-192.png`, `icon-512.png`: instalação como aplicativo.
- Publicado pelo GitHub Pages a partir da branch `main`, pasta raiz.
- Backups: branches `backup-v1-estavel` e `backup-v2-estavel`.

## O que o app tem
Volume, pan, mudo, solo e armar por canal. Efeitos por canal (pré-amplificador, equalizador, delay, chorus), presets de efeitos, copiar e restaurar efeitos, ouvir sem efeitos. Gravação em um ou vários canais armados (entradas separadas com placa de 2 canais), com contagem e metrônomo. Edição (marcar, cortar, copiar, colar, silenciar, desfazer). Afinação de voz. Reverb de voz (cadeia de 4 módulos). Master (equalizador, compressor, reverb leve, limitador). Exportar WAV e MP3. Projetos (salvar, abrir, exportar, importar). Visualizações: Faixas, Compacto, Lista, Lado a lado, Um canal por vez, Mesa vertical. Instruções do aplicativo dentro do app.

## Regras do projeto
- Nunca perder a acessibilidade: controles nativos, valores falados, foco estável.
- Qualquer mudança no app deve atualizar o tutorial "Instruções do aplicativo".
- Um código só para computador e celular.
- Testar com Playwright em celular em pé, deitado e computador.

## Preferências do autor (valem para qualquer conversa nova)
- O autor usa leitor de tela (NVDA e TalkBack) e fala as mensagens por voz, então pode haver erros de digitação. Entenda pelo contexto.
- O que o leitor de tela fala é mais importante do que o que aparece na tela. Nomes de botões claros e curtos, valores falados em português.
- Tela limpa: sem textos de apoio ou frases explicativas soltas. As explicações ficam em "Instruções do aplicativo".
- Pouca rolagem. Opções que não são usadas o tempo todo ficam dentro de um menu fechado (lista, tela própria com botão Fechar), não soltas na tela.
- O botão Gravar fica sempre à vista, no topo, e o foco do leitor fica nele ao gravar e parar. O mesmo vale para o Tocar.
- O gesto de voltar do Android deve fechar só a tela aberta, sem sair do app.
- Botões em ordem lógica, mesma ordem visual e de leitura. Botões relacionados juntos (Voltar e Avançar).
- Presets e escolhas em lista fechada, não em muitos botões.
- Efeitos são por canal. O reverb de voz vale para um canal só de cada vez.
- Respostas curtas e claras, passo a passo quando for explicar. Sem termos em inglês ou técnicos demais.
- Usa a versão gratuita do Claude: juntar vários pedidos numa mudança só, evitar trabalho repetido.
- Avisar sempre que um aplicativo instalado só pega a versão nova ao fechar e abrir de novo.

## Versões
- Versão atual: 1.0. Número e "Novidades" ficam no fim das Instruções do aplicativo (em index.html).
- Plano: o app oficial (raiz do site) muda só no lançamento mensal. As novidades são testadas antes em uma cópia de teste, em uma pasta com nome reservado do mesmo site, que se instala como "SL-Mix Teste". A cópia tem seu próprio sw.js e cache. Ao lançar, copiar o index.html aprovado para a raiz, subir o número da versão, atualizar "Novidades" e marcar a release.
- O endereço do app oficial deve ser trocado para o nome sl-mix (renomear o repositório). Quem usava o link antigo precisa instalar de novo, e projetos devem ser exportados antes.

## Texto de abertura (também no começo das Instruções e para o APK)
O SL-Mix é o aplicativo ideal para os amantes da produção de áudio, desenvolvido para atender tanto profissionais quanto entusiastas do som.
Com uma interface simples, intuitiva e muito fácil de usar, o aplicativo oferece um console prático e eficiente para criação de vinhetas, comerciais, gravações de músicas, edições e muito mais.
Acessibilidade em Primeiro Lugar: pensado para facilitar o dia a dia da comunidade, o SL-Mix foi especialmente desenvolvido com foco total em acessibilidade, com suporte otimizado para TalkBack e NVDA, permitindo que pessoas com deficiência visual naveguem e produzam seus projetos com total autonomia e precisão.
Destaques: Interface Simples e Prática; 100% Acessível; Versátil; Para Todos.
Idealizado e Desenvolvido por: Gutenberg Guerra Lima

## Planos futuros (conversados, nada disso foi programado ainda)
1. Publicar na Play Store: empacotar a versão oficial como APK. Preferência: arquivos dentro do APK (funciona sem internet e permite repositório privado) ou TWA. Precisa de conta de desenvolvedor, e-mail do projeto, política de privacidade e termos de uso.
2. Tela de termos de uso e licença na primeira abertura, com aceite; reaparece quando os termos mudam. Usar o texto de abertura acima na descrição da loja.
3. Monetização por assinatura da Play Store (mensal, 3 meses, 6 meses e anual; também considerar plano pré-pago), com teste grátis de 7 dias. O básico (mixar, cortar, emendar, ouvir) pode ficar livre. Valores ainda a decidir. O app deve continuar funcionando para quem já o tem se o autor parar de atualizar; avisar antes de descontinuar.
4. Linha do tempo com as ondas dos áudios, para quem enxerga, como uma visualização a mais. Só entra se for acessível ao leitor de tela, com descrição falada de cada trecho.
5. Edição de vídeo, em etapas (versão 2.0): primeiro importar vídeo, mixar o áudio na mesa e exportar o vídeo com o novo áudio.
6. Idiomas: primeiro extrair todos os textos do código para listas de tradução, depois inglês, depois espanhol e outros. Informar o idioma ao leitor de tela.
7. Programa separado para Windows para aplicar plugins VST3 (biblioteca pedalboard, em Python), processando arquivos e exportando WAV, com controles acessíveis a partir dos parâmetros do plugin. Só se o autor pedir.
8. Lançamento mensal: as novidades são testadas na cópia de teste (SL-Mix Teste) e passam para o app oficial uma vez por mês, com número de versão e "Novidades" nas Instruções.

## Ideias de atualizações (banco de ideias, não programadas)
Para mostrar movimento aos clientes: tela "Novidades" na primeira abertura após cada atualização; botão "Enviar sugestão" que abre o e-mail do projeto; lista "Em breve" nas Instruções.

Dia a dia: renomear canais (o leitor fala o nome); salvar automático; compartilhar a mixagem pelo Android; duplicar canal e copiar trecho entre canais; mais de seis canais (8 ou 12).

Edição: fade de entrada e de saída; normalizar volume; repetir trecho (loop); marcadores com nome falados; dividir e mover trechos; mudar a velocidade sem mudar o tom; cortar silêncios automaticamente.

Efeitos: compressor e gate por canal; de-esser; limpeza de ruído da voz; reverb por canal com nível próprio; ducking automático da trilha quando a voz fala.

Vinhetas e comerciais: modelos de projeto (vinheta, comercial de 30 s, podcast); biblioteca de efeitos sonoros livres de direitos; medidor e ajuste de loudness para rádio e podcast, com o nível falado.

Gravação: medidor falado antes de gravar ("sinal bom", "alto demais"); regravar só um trecho (punch in); pré-roll.

Arquivos: exportar cada canal separado; formatos M4A, FLAC e OGG.

Acessibilidade: sons curtos de confirmação opcionais; atalhos de teclado personalizáveis; aviso falado contínuo do nível de um canal.

Calendário sugerido: 1.1 Novidades, renomear canais, salvar automático, fade e normalizar. 1.2 compressor e gate por canal, exportar canais separados, compartilhar. 1.3 marcadores falados, loudness, modelos de projeto. Depois: linha do tempo, vídeo e idiomas.

## Estado atual: versão 1.1 de teste (out/2026)
Publicada só na cópia de teste (pasta `teste-7k2m9x`). A raiz continua na 1.0 até o lançamento mensal.
Novidades da 1.1: botão Efeitos em cada canal, que abre a tela de efeitos do canal com a lista fechada (pré-amplificador, equalizador, delay, chorus, reverb de voz, afinação de voz; todos opcionais); reverb de voz com envio por canal ("Envio ao reverb", 0 a 100) e ajustes gerais compartilhados; as seções soltas Afinação de voz e Reverb de voz saíram da tela; nome do canal à escolha (campo "Nome do canal" em Ajustes e efeitos; vale para botões, listas, mensagens e projetos); mesa abre sem canais com Adicionar canal e Remover canal (máximo 6); menu Projetos reordenado (Abrir, Novo, Salvar, Exportar e Importar); botão Editar áudio em cada canal (tela própria com início e fim digitados, passos, cortar, copiar, colar, desfazer, Inserir arquivo no cursor para emendar, Colocar arquivo a partir do cursor para locução sobre trilha, e Separar em faixas: divisões marcadas ouvindo ou por silêncio, salvas em ZIP de WAV).
Pendente: o autor testar com TalkBack e NVDA; ajustes pedidos por ele; depois lançar como oficial.

## Código-fonte (pasta `fonte`)
- `fonte/app-body.html`: fonte do app (um IIFE em JavaScript, funções puras entre `/*PURE-START*/` e `/*PURE-END*/`).
- `fonte/build.py`: gera `site/index.html` e a cópia de teste. Os caminhos dentro dele são `/home/claude/mesa/...`: ajustar para a pasta onde estiver. Precisa de `site/` com sw.js, manifest e ícones (iguais aos da raiz deste repositório). Aumentar o número do cache de teste (`sl-mix-teste-vN`) a cada publicação.
- `fonte/test.js` e `fonte/test_tune.js`: testes das funções puras (`node test.js`).
- `fonte/testes/*.py`: testes de navegador (Playwright; o mais novo é pw_v14.py, rack de efeitos e envio de reverb; pw_v15.py, afinação; pw_v13.py, nome dos canais; pw_v12.py, Editar áudio). Os testes pw2_v2 e pw3_v2 (seções antigas de afinação e reverb) foram removidos. `run6.py arquivo.py` adiciona 6 canais antes de rodar os testes antigos. Servem um site em `/home/claude/mesa/site`.
- Publicar: copiar `site/teste-7k2m9x/*` para a pasta `teste-7k2m9x` deste repositório. O remote precisa continuar `https://github.com/Gutembergguerra/mesa-digital` (o proxy só autoriza o nome antigo; o push redireciona).
