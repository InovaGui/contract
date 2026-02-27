import httpx
import json

class ClicksignClient:
    BASE_URL = "https://sandbox.clicksign.com/api/v2/acceptance_term"
    ACCESS_TOKEN = "5e45a874-d931-4518-9db4-13395ba52cd4"

    async def sendWhatsappAcceptance(self, data):
        payload = {
            "acceptance_term": {
                "name": "Contrato de Empréstimo Consignado",
                "sender_name": "Zé Empresta Soluções Inteligentes",
                "sender_phone": "22999937274",
                "content": (
                    f"Olá {data.signerName}, para dar continuidade à sua solicitação na Zé Empresta, "
                    f"é necessário assinar o contrato do empréstimo. Resumo: valor de {data.requestedAmount}, "
                    f"parcelado em {data.installmentsCount}x de {data.installmentValue}. "
                    f"Taxa de juros de {data.interestRate}% ao mês e CET total de {data.totalCost}. "
                    f"Acesse o link a seguir para ler as cláusulas do contrato de empréstimo: {data.contractUrl}"
                ),
                "signer_phone": data.signerPhone,
                "signer_name": data.signerName,
                "sent_at": data.sentAt
            }
        }
        async with httpx.AsyncClient(timeout=15) as client:
            url = f"{self.BASE_URL}/whatsapps?access_token={self.ACCESS_TOKEN}"
            response = await client.post(url, json=payload, headers={"Accept": "application/json"})
            try:
                return response.json()
            except json.JSONDecodeError:
                return {}

    async def getAcceptance(self, key: str):
        async with httpx.AsyncClient(timeout=15) as client:
            url = f"{self.BASE_URL}/whatsapps/{key}?access_token={self.ACCESS_TOKEN}"
            response = await client.get(url, headers={"Accept": "application/json"})
            try:
                return response.json()
            except json.JSONDecodeError:
                return {}

    async def cancelAcceptance(self, key: str):
        async with httpx.AsyncClient(timeout=15) as client:
            url = f"{self.BASE_URL}/whatsapps/{key}/cancel?access_token={self.ACCESS_TOKEN}"
            response = await client.patch(url, headers={"Accept": "application/json"})
            try:
                return response.json()
            except json.JSONDecodeError:
                return {}
