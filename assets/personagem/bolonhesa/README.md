# Biblioteca de Assets — Nerd Bolonhesa

Catálogo das imagens do personagem (âncora, expressões e poses). As imagens são
geradas **na mão** pelo Pablo no Google AI Studio e **não** ficam no git — só o
`manifest.json` e os scripts são versionados.

## Estrutura

```
ancora/        # a imagem âncora travada (referência-mãe)
expressoes/    # as 12-14 reações
poses/         # as poses de corpo
_revisao/      # saída do contact_sheet.py (gitignored)
```

## Convenção de nomes

```
ancora/bolonhesa_ancora_v1.png
expressoes/bolonhesa_expr_<slug>.png     # ex: bolonhesa_expr_deboche.png
poses/bolonhesa_pose_<slug>.png          # ex: bolonhesa_pose_apontando.png
```

### Slugs das expressões (batem com a bíblia do personagem)

`neutro, deboche, nerd, chocado, olhos-revirados, raiva, rindo, cansado,
pensativo, eureka, facepalm, joinha, desconfiado, aliviado`

## Fluxo de trabalho

1. Gere a imagem no Google AI Studio usando a âncora como referência.
2. Salve na pasta certa com o nome da convenção acima.
3. Rode a folha de contato para bater o olho na consistência:
   ```
   python assets/personagem/bolonhesa/contact_sheet.py
   ```
4. Valide a integridade contra o manifesto:
   ```
   python assets/personagem/bolonhesa/validar.py
   ```

## TODO — Fase 5+ (geração programática)

Quando a geração for plugada no `_stub("visuals")`, criar um `gerar_expressoes.py`
que usa a mesma `GEMINI_API_KEY` mas o **modelo de imagem**
(`gemini-*-flash-image` / Nano Banana), passando a âncora como referência e
iterando sobre os slugs do `manifest.json`. **Não automatizar antes de validar
as 12-14 expressões na mão** — automatizar caro algo ainda não validado.
