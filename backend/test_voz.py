# test_voz.py — rode com: python test_voz.py
from app.providers.chatterbox_tts import ChatterboxProvider

# Só o texto FALADO do roteiro (sem as marcações [visual:])
ROTEIRO = """Tem um framework de Python que viciou metade dos backend devs do mundo. \
E não, não é o Django do seu professor. FastAPI faz três coisas que te deixam \
mal-acostumado pra sempre. Um: ele é rápido. Tipo, rápido de verdade, roda quase \
no nível de Node e Go, o que pra Python é praticamente bruxaria. Dois: type hints. \
Você escreve o tipo dos dados uma vez, e ele valida tudo sozinho. Mandou string onde \
era pra ser número? Ele te xinga antes do usuário. Três, e aqui o povo chora de \
emoção: documentação automática. Você não escreve nenhuma. Ele gera uma página \
interativa inteira sozinho enquanto você toma café."""

provider = ChatterboxProvider()  # voz default (tts_voice_reference vazio)
provider.synthesize(ROTEIRO, "teste_fastapi.wav")
print(f"Pronto! Gerado em teste_fastapi.wav (device: {provider.device})")