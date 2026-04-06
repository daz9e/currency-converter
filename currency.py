from typing import Dict
import requests
import os

# Поддерживаемые валюты
CURRENCIES = {
    'RSD': '🇷🇸 Сербские динары',
    'UAH': '🇺🇦 Гривны',
    'RUB': '🇷🇺 Рубли',
    'EUR': '🇪🇺 Евро'
}

# API для получения курсов валют (можно использовать любой другой)
EXCHANGE_API_URL = "https://api.exchangerate-api.com/v4/latest/EUR"


class CurrencyConverter:
    def __init__(self):
        self.rates = {}
        self._update_rates()
    
    def _update_rates(self):
        """Обновить курсы валют"""
        try:
            response = requests.get(EXCHANGE_API_URL, timeout=5)
            data = response.json()
            
            if 'rates' in data:
                self.rates = {
                    'EUR': 1.0,
                    'RSD': data['rates'].get('RSD', 117.0),
                    'UAH': data['rates'].get('UAH', 45.0),
                    'RUB': data['rates'].get('RUB', 105.0)
                }
        except Exception as e:
            print(f"Не удалось обновить курсы валют: {e}")
            # Запасные курсы
            self.rates = {
                'EUR': 1.0,
                'RSD': 117.0,
                'UAH': 45.0,
                'RUB': 105.0
            }
    
    def convert(self, amount: float, from_currency: str, to_currency: str) -> float:
        """Конвертировать сумму из одной валюты в другую"""
        if from_currency not in self.rates or to_currency not in self.rates:
            raise ValueError(f"Неподдерживаемая валюта")
        
        # Конвертируем через EUR как базовую валюту
        amount_in_eur = amount / self.rates[from_currency]
        amount_in_target = amount_in_eur * self.rates[to_currency]
        
        return round(amount_in_target, 2)
    
    def convert_to_all(self, amount: float, from_currency: str) -> Dict[str, float]:
        """Конвертировать сумму во все остальные валюты"""
        results = {}
        
        for currency in CURRENCIES.keys():
            if currency != from_currency:
                results[currency] = self.convert(amount, from_currency, currency)
        
        return results
    
    def format_results(self, results: Dict[str, float], source_amount: float, source_currency: str) -> str:
        """Форматировать результаты конвертации для отправки"""
        lines = [f"💱 *{source_amount} {source_currency}* =\n"]
        
        for currency, amount in results.items():
            currency_name = CURRENCIES[currency]
            lines.append(f"• {amount:,.2f} {currency} ({currency_name})")
        
        return "\n".join(lines)
