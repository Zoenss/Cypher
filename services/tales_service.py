"""Personalidade e orientações do Tales, com Gemini estritamente opcional."""

from __future__ import annotations

import requests
import streamlit as st

PERSONALIDADE = (
    "Você é Tales, o assistente simpático e curioso do Cypher, um projeto de "
    "logística reversa de eletrônicos. Responda em português brasileiro, com "
    "clareza, acolhimento e humor discreto. Explique como identificar o aparelho, "
    "informar quantidade e massa total em gramas, entender estimativas de "
    "materiais e valor econômico, e localizar descarte. Nunca invente ficha técnica, "
    "ponto de coleta, cotação ou resultado. Os valores do Cypher são estimativas, "
    "não medições laboratoriais. Não peça dados pessoais nem senhas. Respostas curtas."
)


def resposta_local(pergunta: str) -> str:
    p = pergunta.casefold().strip()
    if any(t in p for t in ("oi", "olá", "ola", "bom dia", "e aí", "quem é")):
        return "Opa! 😄 Eu sou o Tales, seu parceiro no Cypher. Quer descobrir o que seu eletrônico pode ter de recuperável?"
    if any(t in p for t in ("peso", "grama", "quantidade", "unidade")):
        return "Vamos nessa! ⚖️ Informe quantos aparelhos são e o peso total deles em gramas. Por exemplo: 2 celulares, 380 g no total."
    if any(t in p for t in ("api", "não encontrou", "erro", "falhou", "identific")):
        return "Às vezes uma fonte não encontra o modelo. O Cypher tenta alternativas gratuitas e mostra quando a ficha é incerta. Você pode conferir o nome exato do aparelho. 🔎"
    if any(t in p for t in ("valor", "preço", "dinheiro", "econôm")):
        return "O valor econômico é uma estimativa baseada na massa e nos materiais. Não é uma oferta de compra nem uma cotação garantida, beleza? 💰"
    if any(t in p for t in ("descar", "coleta", "recic", "onde levar")):
        return "Na seção 'Onde descartar', informe sua cidade ou CEP. Confira se o local aceita seu tipo de equipamento antes de sair de casa. ♻️"
    if any(t in p for t in ("funciona", "começar", "usar", "análise", "analise")):
        return "É simples! 1️⃣ Diga o modelo, 2️⃣ informe a quantidade, 3️⃣ pese tudo em gramas, 4️⃣ inicie a análise. Eu ajudo a entender o resultado!"
    return "Boa pergunta! 😊 Posso te orientar sobre a análise, peso, identificação, valor estimado e descarte. Qual dessas etapas você quer entender?"


def gemini_disponivel() -> bool:
    """Nunca ativa por padrão. Exige chave e opção explícita do proprietário."""
    try:
        return (str(st.secrets.get("GEMINI_FREE_TIER_ENABLED", "false")).lower() == "true"
                and bool(st.secrets.get("GEMINI_API_KEY")))
    except Exception:
        return False


def responder(pergunta: str, usar_gemini: bool = False) -> tuple[str, str]:
    pergunta = pergunta.strip()[:500]
    if not pergunta:
        return "Me conta sua dúvida! 😄", "local"
    if not usar_gemini or not gemini_disponivel():
        return resposta_local(pergunta), "local"
    # O modelo e a cota pertencem ao plano configurado na conta Google. O
    # Cypher não ativa faturamento nem faz upgrade automaticamente.
    try:
        resposta = requests.post(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent",
            headers={"x-goog-api-key": str(st.secrets["GEMINI_API_KEY"])},
            json={"systemInstruction": {"parts": [{"text": PERSONALIDADE}]},
                  "contents": [{"role": "user", "parts": [{"text": pergunta}]}],
                  "generationConfig": {"maxOutputTokens": 250, "temperature": 0.6}},
            timeout=12,
        )
        resposta.raise_for_status()
        partes = resposta.json()["candidates"][0]["content"]["parts"]
        texto = " ".join(str(item.get("text", "")) for item in partes).strip()
        return (texto or resposta_local(pergunta)), "gemini"
    except (requests.RequestException, KeyError, ValueError, IndexError, TypeError):
        return resposta_local(pergunta), "local (Gemini indisponível)"
