"""Filtro genérico por chave dentro de um campo JSONB.

Uso: ``GET /api/produtos/?atributos__cor=azul`` ou
``GET /api/produtos/?atributos__peso_kg__lte=2`` ou, para chaves aninhadas,
``?atributos__dimensoes__altura=30``.

Igualdade usa o operador de contenção do PostgreSQL (``@>``), que é o que o
índice GIN acelera (``atributos @> '{"cor": "azul"}'``). Comparações
(``gt/gte/lt/lte``) e ``icontains`` extraem a chave e não usam o GIN.

Somente chaves alfanuméricas e lookups da lista abaixo são aceitos, então
não há como o cliente montar um filtro arbitrário no ORM.
"""
import json
import re

from django.db.models import Q
from rest_framework.exceptions import ValidationError

CHAVE_RE = re.compile(r"^[A-Za-z0-9_]+$")
LOOKUPS_PERMITIDOS = {"gt", "gte", "lt", "lte", "icontains"}


def _converter(valor):
    """'azul' -> 'azul', '2' -> 2, 'true' -> True, '2.5' -> 2.5."""
    try:
        return json.loads(valor)
    except (TypeError, ValueError):
        return valor


def _aninhar(partes, valor):
    """['dimensoes', 'altura'], 30 -> {'dimensoes': {'altura': 30}}."""
    documento = valor
    for chave in reversed(partes):
        documento = {chave: documento}
    return documento


class JSONFieldFilterMixin:
    """Aplica filtros ``<json_field>__<chave>[__<lookup>]=<valor>``."""

    json_field = None  # sobrescrever na view

    def filter_json(self, queryset):
        prefixo = f"{self.json_field}__"
        contem = f"{self.json_field}__contains"
        for param, bruto in self.request.query_params.items():
            if not param.startswith(prefixo):
                continue
            partes = param[len(prefixo):].split("__")
            lookup = None
            if len(partes) > 1 and partes[-1] in LOOKUPS_PERMITIDOS:
                lookup = partes.pop()
            if not partes or not all(CHAVE_RE.match(p) for p in partes):
                raise ValidationError(
                    {param: "Chave JSON inválida (use letras, números e _)."}
                )

            if lookup:
                caminho = "__".join([self.json_field, *partes, lookup])
                valor = bruto if lookup == "icontains" else _converter(bruto)
                queryset = queryset.filter(**{caminho: valor})
                continue

            # Igualdade => contenção (@>), servida pelo índice GIN.
            # Aceita o valor tipado (42, true) e como texto ("42"), pois o
            # JSON do produto pode guardar qualquer um dos dois.
            tipado = _converter(bruto)
            condicao = Q(**{contem: _aninhar(partes, tipado)})
            if tipado != bruto:
                condicao |= Q(**{contem: _aninhar(partes, bruto)})
            queryset = queryset.filter(condicao)
        return queryset
