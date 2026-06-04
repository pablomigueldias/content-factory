# Gordão Bolonhesa — Plano de Execução

> Estado do projeto após a sessão de desenvolvimento do backend.
> Documento de acompanhamento: o que **já está pronto no código** e o que **você precisa fazer** (manual).
> Para a visão/identidade do canal, ver o documento-mestre do projeto (personagem, tom, fórmula).

---

## 1. Onde estamos

A **esteira de produção** do Content Factory (backend) foi totalmente alinhada com a
identidade do Bolonhesa. O pipeline hoje é:

```
research → editorial → scripting → factcheck → narration
(fatos)    (persona)    (roteiro)   (valida)    (voz)
```

Cada etapa já reflete o plano:

- **editorial** gera a persona, tese e gancho na **voz do Bolonhesa** (não mais "Discovery genérico").
- **scripting** escreve o roteiro na **fórmula fixa de 4 batidas** (Gancho → Densidade → Ahá → Retenção),
  com cada cena separada em duas camadas: **bravata** (deboche/ego) e **verdade_tecnica** (o fato correto).
- **factcheck** valida **apenas a verdade técnica** contra os fatos verificados (a bravata é humor, não fato).
- **narration** gera a voz com **Chatterbox**, com suporte a **voz de referência clonada** e
  **controle de entonação** (cadência arrastada/debochada) via configuração.

**Estado técnico:** 64 testes passando, migrações de banco aplicadas e validadas.

---

## 2. O que já foi feito (código) — 7 commits

| # | Commit | O que entrega |
|---|--------|---------------|
| 1 | `split scene narration into bravata + verdade_tecnica` | Roteiro em 2 camadas. A **Regra de Ouro**: a burrice é da persona (bravata), o técnico está sempre certo (verdade_tecnica). A narração falada é a concatenação das duas. |
| 2 | `bake Gordão Bolonhesa persona into the editorial prompt` | O ângulo editorial agora nasce na voz do Bolonhesa (nerd arrogante-inseguro, deboche), não num tom neutro. |
| 3 | `track backend models package, ignored by mistake` | **Bug de repo corrigido:** `app/models/scene.py` e `editorial.py` estavam fora do git (a regra `models/` do `.gitignore`, pensada pros pesos de IA, engolia o código). Resgatados. |
| 4 | `fact-check the technical layer instead of the full narration` | O factcheck passa a validar só a `verdade_tecnica`. Coluna nova no banco + migração. Cenas antigas caem de volta pra narração completa. |
| 5 | `persist the bravata layer on the Scene` | A `bravata` virou coluna própria. As duas camadas ficam separadas no banco → permite **trocar a expressão na batida** (cara de deboche na bravata, cara de explicação na verdade técnica). |
| 6 | `expose Chatterbox tone knobs for the Bolonhesa voice` | Controles de **entonação** (`exaggeration`, `cfg_weight`, `temperature`) expostos via `.env`. Calibrar o tom virou ajuste de config, sem mexer em código. |
| 7 | `script with the fixed 4-beat short formula` | Substituiu o sorteio de estrutura genérica pela **fórmula fixa de 4 batidas**. Roteiro travado em 4-6 cenas, ~30-60s (formato short). |

### Como o roteiro fica estruturado agora

Cada **cena** gerada tem:

- `bravata` — a fala arrogante/debochada da persona (humor).
- `verdade_tecnica` — o fato correto (o que o espectador aprende; é o que o factcheck valida).
- `narration` — bravata + verdade técnica concatenadas (é o que vai pro TTS).
- `visual_description` — o que aparece na tela.
- `duration_seconds` — duração da cena (2-60s).

A primeira cena começa com o **gancho**; as do meio são **densidade** (fato + ironia); a penúltima
é o **ahá** (a virada onde se aprende); a última é **retenção** (ponta solta pro próximo vídeo).

---

## 3. O que VOCÊ tem que fazer

O código chegou no limite do que resolve sozinho. Daqui pra frente o que destrava o projeto é
**manual/criativo** — não depende de mais commits.

### ✅ Fase 0 — Personagem `[PRÓXIMA]`

- [ ] **Cravar a ferramenta** de personagem (testar 1-2: FlexClip / Nano Banana / LlamaGen e decidir).
- [ ] Gerar a **imagem âncora** do Bolonhesa — traço **original e identificável**.
      ⚠️ **NÃO** imitar o estilo visual do South Park (risco de copyright/desmonetização).
- [ ] Montar a **biblioteca de 8-12 expressões** (feliz, deboche, choque, 🤓, raiva de jogo, etc.).
- [ ] Guardar os assets fora do git (a pasta `media/`/`assets_cache/` já é ignorada — coloca lá).

### ⏳ Fase 1 — Voz

O código já está **100% pronto** pra isso. O que falta é seu ouvido:

- [ ] **Gravar** um WAV de referência no tom do Bolonhesa: pausado, arrastado, debochado.
- [ ] Apontar o arquivo no `.env`:
      ```
      TTS_VOICE_REFERENCE="/caminho/para/voz_bolonhesa.wav"
      ```
- [ ] **Calibrar a entonação** ouvindo o resultado e ajustando no `.env`:
      ```
      TTS_CFG_WEIGHT=0.5     # menor = fala mais lenta/arrastada (testa 0.3)
      TTS_EXAGGERATION=0.5   # maior = mais expressivo/debochado (testa 0.6-0.7)
      TTS_TEMPERATURE=0.8    # variação da entonação
      ```
- [ ] Repetir até "a entonação bater" (esse ajuste fino é só seu — o código não decide isso).

### ⏳ Fase 2 — Primeiro short (na mão)

- [ ] Rodar o pipeline num tema real e pegar o roteiro + áudios gerados.
- [ ] Montar no **CapCut**: corte seco, ritmo apertado, legenda karaokê, trocar expressão na batida.
- [ ] **NÃO automatizar ainda** — o objetivo é sentir o formato.

### ⏳ Fase 3 — Reps

- [ ] 1 short por semana, por 8-12 semanas. Aprender edição, medir retenção.
- [ ] **Constância é A variável** — sem 1/semana consistente, nada funciona.

---

## 4. Como rodar o pipeline (quando quiser testar o roteiro de verdade)

Pré-requisitos:

- [ ] `GEMINI_API_KEY` preenchida no `backend/.env` (copia de `.env.example`).
- [ ] Postgres de pé (via `docker-compose up -d` na raiz).
- [ ] Migrações aplicadas: `cd backend && poetry run alembic upgrade head`.

Rodar os testes pra confirmar que está tudo são:

```bash
cd backend && poetry run pytest -q
```

> Quando quiser, posso te ajudar a disparar o pipeline ponta-a-ponta num tema de teste pra ver o
> roteiro do Bolonhesa saindo — é só pedir.

---

## 5. Decisões em aberto (do documento-mestre)

- [ ] **Nome final:** "Gordão Bolonhesa" vs "Nerd Bolonhesa" (sugestão atual: Gordão).
- [ ] **Foco do conteúdo:** iniciante puro ou mistura iniciante + zoação geek.
- [ ] **Ferramenta de personagem:** testar 1-2 e cravar (ver Fase 0).

---

## 6. Honestidades registradas (não esquecer)

- Constância é A variável. Sem 1/semana, nada funciona.
- Trocar expressão na batida ainda é trabalho manual por vídeo (leve, mas não zero).
- Renda é médio prazo. YPP: 1000 inscritos + 4000h.
- O diferencial é **profundidade técnica real + persona** — não "AI slop".
- Validar barato (na mão) antes de automatizar caro (código). Sempre.
- A voz default do Chatterbox é morta; a alma vem da **referência gravada**.
