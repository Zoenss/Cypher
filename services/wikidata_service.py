"""Identificação complementar pela Wikidata (dados CC0, sem chave)."""

from __future__ import annotations

import re
import unicodedata
from typing import Any

import requests
import streamlit as st

API = "https://www.wikidata.org/w/api.php"
HEADERS = {"User-Agent": "Cypher-TCC/1.0 (projeto educacional)", "Accept": "application/json"}


class WikidataError(RuntimeError):
    pass


def _tokens(nome: str) -> set[str]:
    texto = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode().lower()
    return set(re.findall(r"[a-z0-9]+", texto))


def _corresponde(consulta: str, rotulo: str) -> bool:
    buscados, encontrados = _tokens(consulta), _tokens(rotulo)
    ignorar = {"galaxy", "5g", "4g", "phone", "smartphone"}
    essenciais = buscados - ignorar
    return bool(essenciais) and essenciais.issubset(encontrados)


@st.cache_data(ttl=86400, show_spinner=False)
def buscar_modelo_wikidata(nome: str) -> dict[str, Any]:
    """Busca um rótulo exato/compatível, sem assumir especificações técnicas."""
    try:
        resposta = requests.get(
            API,
            params={"action": "wbsearchentities", "search": nome, "language": "en", "format": "json", "limit": 8},
            headers=HEADERS,
            timeout=10,
        )
        resposta.raise_for_status()
        dados = resposta.json()
        encontrados = dados.get("search", [])
        if not isinstance(encontrados, list):
            raise WikidataError("Resposta da Wikidata inesperada.")
        for item in encontrados:
            if not isinstance(item, dict):
                continue
            rotulo = str(item.get("label", ""))
            codigo = str(item.get("id", ""))
            if _corresponde(nome, rotulo) and re.fullmatch(r"Q[1-9]\d*", codigo):
                return {"encontrado": True, "fonte": "Wikidata", "modelo": rotulo,
                        "identificador": codigo, "url": f"https://www.wikidata.org/wiki/{codigo}",
                        "descricao": item.get("description", ""), "ficha_tecnica": False}
        return {"encontrado": False, "fonte": "Wikidata"}
    except (requests.RequestException, ValueError, TypeError) as erro:
        raise WikidataError("Consulta gratuita à Wikidata indisponível.") from erro
