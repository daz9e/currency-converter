# Money Convert

Telegram bot for currency conversion between RSD, UAH, RUB and EUR.

Send a number to convert from your default currency, or specify one explicitly: `100 EUR`.

## Setup

Set `TELEGRAM_BOT_TOKEN` and optionally `DEFAULT_CURRENCY` (defaults to `EUR`).

### Docker

```bash
cp .env.example .env
docker-compose up -d
```

### NixOS

```nix
services.money-convert = {
  enable = true;
  tokenFile = config.age.secrets.money-convert-token.path;
  defaultCurrency = "RSD";
};
```
