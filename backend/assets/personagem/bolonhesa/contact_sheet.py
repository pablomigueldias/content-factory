"""Monta uma folha de contato das imagens do Bolonhesa para revisão de consistência."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE = Path(__file__).parent
PASTAS = ["ancora", "expressoes", "poses"]
SAIDA = BASE / "_revisao" / "folha_contato.png"

CELULA = 256          # tamanho de cada miniatura (px)
COLUNAS = 4
PAD = 16
RODAPE = 24           # espaço pro nome embaixo


def coletar():
    imgs = []
    for pasta in PASTAS:
        for p in sorted((BASE / pasta).glob("*.png")):
            imgs.append(p)
    return imgs


def main():
    imgs = coletar()
    if not imgs:
        print("Nenhuma imagem .png encontrada. Gere as imagens no AI Studio primeiro.")
        return

    linhas = (len(imgs) + COLUNAS - 1) // COLUNAS
    largura = COLUNAS * (CELULA + PAD) + PAD
    altura = linhas * (CELULA + RODAPE + PAD) + PAD

    folha = Image.new("RGB", (largura, altura), "white")
    draw = ImageDraw.Draw(folha)
    try:
        fonte = ImageFont.truetype("DejaVuSans.ttf", 14)
    except OSError:
        fonte = ImageFont.load_default()

    for i, p in enumerate(imgs):
        col, lin = i % COLUNAS, i // COLUNAS
        x = PAD + col * (CELULA + PAD)
        y = PAD + lin * (CELULA + RODAPE + PAD)
        try:
            thumb = Image.open(p).convert("RGBA")
            thumb.thumbnail((CELULA, CELULA))
            fundo = Image.new("RGBA", (CELULA, CELULA), (240, 240, 240, 255))
            ox = (CELULA - thumb.width) // 2
            oy = (CELULA - thumb.height) // 2
            fundo.alpha_composite(thumb, (ox, oy))
            folha.paste(fundo.convert("RGB"), (x, y))
        except Exception as e:
            draw.rectangle([x, y, x + CELULA, y + CELULA], outline="red")
            draw.text((x + 4, y + 4), f"ERRO: {e}", fill="red", font=fonte)
        draw.text((x, y + CELULA + 4), p.name, fill="black", font=fonte)

    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    folha.save(SAIDA)
    print(f"Folha de contato salva em: {SAIDA}  ({len(imgs)} imagens)")


if __name__ == "__main__":
    main()
