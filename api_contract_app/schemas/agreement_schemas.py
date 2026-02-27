from pydantic import BaseModel

class AgreementSignatureRequest(BaseModel):
    signerName: str
    signerPhone: str
    requestedAmount: str
    installmentsCount: str
    installmentValue: str
    interestRate: str
    totalCost: str
    contractUrl: str
    sentAt: str