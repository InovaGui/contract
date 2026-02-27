from integrations.clicksign_client import ClicksignClient

class ClicksignService:
    def __init__(self):
        self.client = ClicksignClient()

    async def sendAgreementForSignature(self, data, request):
        response = await self.client.sendWhatsappAcceptance(data)
        result = response.get("acceptance_term") or response.get("acceptance") or {}
        return result.get("key")

    async def getStatus(self, signatureDocumentId: str):
        response = await self.client.getAcceptance(signatureDocumentId)
        data = response.get("acceptance") or response.get("acceptance_term") or {}
        
        return {
            "signatureDocumentId": data.get("key"),
            "status": data.get("status"),
            "signerPhone": data.get("signer_phone")
        }

    async def cancel(self, signatureDocumentId: str):
        response = await self.client.cancelAcceptance(signatureDocumentId)
        data = response.get("acceptance") or response.get("acceptance_term") or {}
        
        return {
            "signatureDocumentId": data.get("key"),
            "status": data.get("status"),
            "signerPhone": data.get("signer_phone")
        }