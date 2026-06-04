"""Valida a integridade da biblioteca do Bolonhesa contra o manifest.json.

Checa duas coisas:
  (1) todo arquivo citado no manifesto existe no disco;
  (2) todo PNG no disco está no manifesto (não tem "órfão").

Sai com código != 0 se algo falhar — pra plugar em CI depois.
"""
import json
import sys
from pathlib import Path

BASE = Path(__file__).parent
MANIFESTO = BASE / "manifest.json"
PASTAS = ["ancora", "expressoes", "poses"]


def arquivos_do_manifesto(dados):
    """Retorna o conjunto de caminhos (relativos à BASE) citados no manifesto."""
    refs = set()
    if dados.get("ancora"):
        refs.add(dados["ancora"])
    for item in dados.get("ancora_views", []):
        refs.add(item["arquivo"])
    for item in dados.get("expressoes", []):
        refs.add(item["arquivo"])
    for item in dados.get("poses", []):
        refs.add(item["arquivo"])
    return refs


def pngs_no_disco():
    """Retorna o conjunto de PNGs presentes no disco (relativos à BASE)."""
    no_disco = set()
    for pasta in PASTAS:
        for p in (BASE / pasta).glob("*.png"):
            no_disco.add(p.relative_to(BASE).as_posix())
    return no_disco


def main():
    if not MANIFESTO.exists():
        print(f"ERRO: manifesto não encontrado em {MANIFESTO}")
        return 1

    dados = json.loads(MANIFESTO.read_text(encoding="utf-8"))
    refs = arquivos_do_manifesto(dados)
    no_disco = pngs_no_disco()

    faltando = sorted(r for r in refs if not (BASE / r).exists())
    orfaos = sorted(no_disco - refs)

    if faltando:
        print(f"FALTANDO ({len(faltando)}) — citados no manifesto, ausentes no disco:")
        for r in faltando:
            print(f"  - {r}")
    if orfaos:
        print(f"ÓRFÃOS ({len(orfaos)}) — no disco, mas fora do manifesto:")
        for r in orfaos:
            print(f"  - {r}")

    total = len(refs)
    presentes = total - len(faltando)
    print(f"\nResumo: {presentes}/{total} arquivos do manifesto presentes; "
          f"{len(orfaos)} órfão(s).")

    if faltando or orfaos:
        return 1
    print("OK — biblioteca íntegra.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
