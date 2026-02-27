from fastapi import APIRouter, Request
from schemas.agreement_schemas import AgreementSignatureRequest
from services.clicksign_service import ClicksignService

router = APIRouter(prefix="/agreements", tags=["Agreements"])
service = ClicksignService()

@router.post("/signature/whatsapp")
async def requestAgreementSignature(request: Request, data: AgreementSignatureRequest):
    signatureDocumentId = await service.sendAgreementForSignature(data, request)
    return {
        "signatureDocumentId": signatureDocumentId
    }

@router.get("/signature/whatsapp/status/{signatureDocumentId}")
async def getAgreementStatus(signatureDocumentId: str):
    return await service.getStatus(signatureDocumentId)

@router.patch("/signature/whatsapp/cancel/{signatureDocumentId}")
async def cancelAgreement(signatureDocumentId: str):
    return await service.cancel(signatureDocumentId)