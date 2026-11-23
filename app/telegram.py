import httpx

from app import config


def enviar_mensagem(texto: str) -> None:
    if not config.TELEGRAM_BOT_TOKEN or not config.TELEGRAM_CHAT_ID:
        raise RuntimeError("Configure TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID no .env")

    url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        resp = httpx.post(
            url,
            json={
                "chat_id": config.TELEGRAM_CHAT_ID,
                "text": texto[:4000],
                "disable_web_page_preview": True,
            },
            timeout=15,
        )
    except httpx.HTTPError as exc:
        # a URL da exceção contém o token: não propagamos a original
        raise RuntimeError(f"Falha de rede ao falar com o Telegram ({type(exc).__name__})") from None

    if resp.status_code != 200:
        try:
            descricao = resp.json().get("description", "")
        except ValueError:
            descricao = ""
        raise RuntimeError(f"Telegram recusou o envio: HTTP {resp.status_code} - {descricao}")