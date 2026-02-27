from pydantic import BaseModel, model_validator
from typing import List, Optional
import json

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

    @model_validator(mode='before')
    @classmethod
    def parse_simulation_if_string(cls, data):
        if isinstance(data, dict) and 'simulation' in data:
            if isinstance(data['simulation'], str):
                try:
                    data['simulation'] = json.loads(data['simulation'])
                except Exception:
                    pass
        return data