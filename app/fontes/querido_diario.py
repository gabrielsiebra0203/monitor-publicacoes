import time
from datetime import date

import httpx

from app import config
from app.fontes.base import PublicacaoEncontrada

MAX_PAGINAS = 20
STATUS_TEMPORARIOS = {429, 502, 503, 504}
TENTATIVAS = 3


class QueridoDiario:
    nome = "querido_diario"

    def __init__(self, territory_ids=None, base_url=None, client=None, pausa=1.0, espera=2.0):
        self.territory_ids = territory_ids or config.QD_TERRITORY_IDS
        self.base_url = base_url or config.QD_BASE_URL
        self.client = client or httpx.Client(timeout=30)
        self.pausa = pausa
        self.espera = espera

    def _get(self, url: str, params: dict) -> httpx.Response:
        ultimo_erro: Exception | None = None
        for tentativa in range(1, TENTATIVAS + 1):
            try:
                resp = self.client.get(url, params=params)
                if resp.status_code in STATUS_TEMPORARIOS:
                    resp.raise_for_status()
                resp.raise_for_status()
                return resp
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code not in STATUS_TEMPORARIOS:
                    raise  # erro de verdade (ex.: 400, 404): não adianta repetir
                ultimo_erro = exc
            except httpx.TransportError as exc:
                ultimo_erro = exc
            time.sleep(self.espera * tentativa)
        raise ultimo_erro    

    def buscar(self, termo: str, desde: date, ate: date) -> list[PublicacaoEncontrada]:
        resultados: list[PublicacaoEncontrada] = []
        tamanho = 50
        offset = 0

        for _ in range(MAX_PAGINAS):
            params = {
                "territory_ids": self.territory_ids,
                "published_since": desde.isoformat(),
                "published_until": ate.isoformat(),
                "querystring": f'"{termo}"',
                "excerpt_size": 400,
                "number_of_excerpts": 2,
                "size": tamanho,
                "offset": offset,
                "sort_by": "descending_date",
            }
            resp = self._get(f"{self.base_url}/gazettes", params)
            dados = resp.json()
            gazettes = dados.get("gazettes", [])

            for g in gazettes:
                edicao = g.get("edition")
                resultados.append(
                    PublicacaoEncontrada(
                        fonte=self.nome,
                        municipio=g.get("territory_name", ""),
                        data_publicacao=date.fromisoformat(g["date"]),
                        edicao=str(edicao) if edicao else None,
                        url=g["url"],
                        trechos=[t.strip() for t in g.get("excerpts", [])],
                    )
                )

            offset += tamanho
            if not gazettes or offset >= dados.get("total_gazettes", 0):
                break
            time.sleep(self.pausa)  # respeita o limite de requisições da API

        return resultados