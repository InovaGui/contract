from fastapi import APIRouter
from schemas.contract_schemas import GenerateContractRequest
from services.pdf_service import PDFService

router = APIRouter(prefix="/contracts", tags=["Contracts"])
pdf_service = PDFService()

@router.post("/generate")
async def generate_contract(data: GenerateContractRequest):
    return await pdf_service.generate_and_upload(data)