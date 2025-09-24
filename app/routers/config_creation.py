from fastapi import APIRouter
from schemas.terragrunt_example import vpc
from library.json2hcl import generate_terragrunt_hcl_from_model
from pathlib import Path
import os

router = APIRouter()


@router.post("/tf/vpc")
async def create_vpc(payload: vpc):
    # Resolve destination path and ensure directory exists
    output_path = Path(os.path.expanduser(payload.conf_path)).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Generate HCL from the nested Terragrunt module and write to the requested path
    hcl_content = generate_terragrunt_hcl_from_model(payload.terragrunt, str(output_path))

    return {
        "hcl_path": str(output_path),
        "hcl": hcl_content,
        "payload": payload.model_dump(),
    }
