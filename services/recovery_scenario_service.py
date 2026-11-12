"""Cenários hipotéticos de recuperação; não representam rendimento industrial medido."""
from __future__ import annotations

import math
from typing import Any

from services.economic_service import obter_preco_por_grama, normalizar_material


def simular_recuperacao(
    materiais: list[dict[str, Any]],
    rendimentos: dict[str, float],
    custos_processamento_rs: float = 0.0,
) -> dict[str, Any]:
    """Simula massas recuperadas e receita bruta potencial com rendimentos [0, 1].

    Rendimentos são hipóteses fornecidas pelo usuário; sem rendimento informado,
    o material não é considerado recuperado. Preços são referências internas.
    """
    custo = float(custos_processamento_rs)
    if not math.isfinite(custo) or custo < 0:
        raise ValueError("O custo de processamento deve ser finito e não negativo.")

    taxas = {}
    for nome, taxa in rendimentos.items():
        valor = float(taxa)
        if not math.isfinite(valor) or not 0 <= valor <= 1:
            raise ValueError(f"Rendimento inválido para {nome}: use um valor entre 0 e 1.")
        taxas[normalizar_material(nome)] = valor

    detalhes = []
    massa_total = 0.0
    massa_recuperada = 0.0
    valor_bruto = 0.0
    for item in materiais:
        nome = normalizar_material(str(item.get("material", "")))
        massa = float(item.get("massa_estimada_g", 0))
        if not math.isfinite(massa) or massa < 0:
            raise ValueError(f"Massa inválida para {nome}.")
        taxa = taxas.get(nome, 0.0)
        recuperada = massa * taxa
        valor = recuperada * obter_preco_por_grama(nome)
        massa_total += massa
        massa_recuperada += recuperada
        valor_bruto += valor
        detalhes.append({
            "material": nome,
            "massa_presente_g": round(massa, 6),
            "rendimento_hipotetico_pct": round(taxa * 100, 2),
            "massa_recuperada_estimada_g": round(recuperada, 6),
            "valor_bruto_potencial_rs": round(valor, 2),
        })

    return {
        "materiais": detalhes,
        "massa_total_g": round(massa_total, 6),
        "massa_recuperada_estimada_g": round(massa_recuperada, 6),
        "taxa_recuperacao_estimada_pct": round(100 * massa_recuperada / massa_total, 2) if massa_total else 0.0,
        "valor_bruto_potencial_rs": round(valor_bruto, 2),
        "custos_processamento_rs": round(custo, 2),
        "saldo_hipotetico_rs": round(valor_bruto - custo, 2),
        "observacao": "Simulação hipotética com preços internos de referência. Não é cotação, receita realizada nem lucro comprovado.",
    }
