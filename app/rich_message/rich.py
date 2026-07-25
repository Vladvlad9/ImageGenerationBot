def rich_msg(image_quality: str, image_aspect_ratio: str) -> str:
    ORDER_RICH_HTML = f"""
    <h1>📖 Пишите запрос на любом языке:</h1>

    <p>
      – Эта модель понимает конкретно каждое ваше слово: на русском, на английском и любом языке
    </p>

    <p>
      – Попросите её, например, создать постер с приглашением на мероприятие (укажите всю информацию о нём)
    </p>

    <table bordered striped>
      <caption>⚙️ Настройки:</caption>
      <tr>
        <th>Качество</th>
        <th>Формат фото</th>
      </tr>
      <tr>
        <td>{image_quality}</td>
        <td>{image_aspect_ratio}</td>
      </tr>
    </table>

    <details>
      <summary>Баланс</summary>
      <p>
        🔹 Баланса хватит на 1 запрос. 1 фото = 6,900 токенов.
      </p>
    </details>
    """
    return ORDER_RICH_HTML
