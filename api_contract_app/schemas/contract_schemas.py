from pydantic import BaseModel
from typing import List, Optional

class InstallmentDetail(BaseModel):
    totalAmount: float
    dueDate: Optional[str]

class SimulationData(BaseModel):
    principalAmount: float
    settledPrincipal: float
    totalPayable: float
    interestRate: float
    installments: List[InstallmentDetail]

class GenerateContractRequest(BaseModel):
    userId: str
    loanId: str
    simulation: SimulationData