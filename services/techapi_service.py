"""Consulta gratuita e conservadora ao catálogo aberto TechAPI.

Dados: GetTechAPI/TechAPI (CC-BY-SA 4.0). Os resultados não verificados
continuam identificados como provisórios e nunca substituem a MobileAPI.
"""

from __future__ import annotations

import re
import unicodedata
from difflib import SequenceMatcher
from typing import Any

import requests
import streamlit as st

REPOSITORY_API = "https://api.github.com/repos/GetTechAPI/TechAPI"
RAW_BASE = "https://raw.githubusercontent.com/GetTechAPI/TechAPI/develop"
BRANDS = {
    "samsung", "apple", "xiaomi", "motorola", "google", "oneplus",
    "oppo", "realme", "vivo", "honor", "huawei", "sony", "nokia",
    "asus", "lenovo", "lg", "nothing", "poco", "redmi",
}
ALIASES = {"iphone": "apple", "pixel": "google", "redmi": "xiaomi", "poco": "xiaomi"}


class TechAPIError(RuntimeError):
    pass


def _slug(texto: str) -> str:
    ascii_texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", ascii_texto.lower()).strip("-")


def _marca(nome: str) -> str | None:
    tokens = _slug(nome).split("-")
    for token in tokens:
        if token in ALIASES:
            return ALIASES[token]
        if token in BRANDS:
            return token
    return None


@st.cache_data(ttl=86400, show_spinner=False)
def _listar_fichas(marca: str) -> list[str]:
    # Navega até a árvore da marca; consultar a raiz recursivamente seria pesado.
    arvore = "develop"
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "Cypher-TCC/1.0"}
    for parte in ("data", "smartphone", marca):
        resposta = requests.get(f"{REPOSITORY_API}/git/trees/{arvore}", headers=headers, timeout=15)
        if resposta.status_code in (403, 429):
            raise TechAPIError("Limite público de consultas da TechAPI/GitHub atingido.")
        resposta.raise_for_status()
        filhos = resposta.json().get("tree", [])
        item = next((i for i in filhos if i.get("path") == parte and i.get("type") == "tree"), None)
        if not item:
            return []
        arvore = item["sha"]
    resposta = requests.get(
        f"{REPOSITORY_API}/git/trees/{arvore}",
        params={"recursive": 1}, headers=headers, timeout=15,
    )
    if resposta.status_code in (403, 429):
        raise TechAPIError("Limite público de consultas da TechAPI/GitHub atingido.")
    resposta.raise_for_status()
    dados = resposta.json()
    if dados.get("truncated"):
        raise TechAPIError("Índice da TechAPI incompleto; consulta ignorada por segurança.")
    return [item["path"] for item in dados.get("tree", [])
            if item.get("type") == "blob" and item.get("path", "").endswith(".json")]


@st.cache_data(ttl=86400, show_spinner=False)
def _ficha(marca: str, caminho: str) -> dict[str, Any]:
    resposta = requests.get(
        f"{RAW_BASE}/data/smartphone/{marca}/{caminho}",
        headers={"User-Agent": "Cypher-TCC/1.0"}, timeout=15,
    )
    resposta.raise_for_status()
    dados = resposta.json()
    if not isinstance(dados, dict):
        raise TechAPIError("Ficha da TechAPI inválida.")
    return dados


def buscar_techapi(nome: str) -> dict[str, Any]:
    """Retorna somente correspondências fortes; não inventa dados ausentes."""
    marca = _marca(nome)
    if not marca:
        return {"encontrado": False, "fonte": "TechAPI"}
    consulta = _slug(nome)
    termo = _slug(nome).split("-")
    termo = [t for t in termo if t not in {marca, "5g", "4g"}]
    if not termo:
        return {"encontrado": False, "fonte": "TechAPI"}
    try:
        caminhos = _listar_fichas(marca)
        candidatos = []
        for caminho in caminhos:
            stem = caminho.rsplit("/", 1)[-1].removesuffix(".json")
            normal = _slug(stem)
            if all(t in normal.split("-") for t in termo):
                candidatos.append((SequenceMatcher(None, consulta, normal).ratio(), caminho))
        if not candidatos:
            return {"encontrado": False, "fonte": "TechAPI"}
        pontuacao, caminho = max(candidatos)
        if pontuacao < 0.72:
            return {"encontrado": False, "fonte": "TechAPI"}
        dados = _ficha(marca, caminho)
        if _marca(str(dados.get("name", ""))) != marca:
            return {"encontrado": False, "fonte": "TechAPI"}
        return {
            "encontrado": True,
            "fonte": "TechAPI",
            "modelo": dados.get("name"),
            "fabricante": marca.title(),
            "peso": dados.get("weight_g"),
            "bateria": dados.get("battery_mah"),
            "ram": dados.get("ram_gb"),
            "armazenamento": dados.get("storage_options_gb"),
            "verificado": bool(dados.get("verified")),
            "confianca_correspondencia": round(pontuacao, 2),
            "atribuicao": "Data from TechAPI (CC-BY-SA 4.0)",
            "source_urls": dados.get("source_urls", []),
        }
    except (requests.RequestException, ValueError, KeyError) as erro:
        raise TechAPIError("Não foi possível consultar a TechAPI.") from erro
