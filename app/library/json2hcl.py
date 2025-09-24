from hcl2.api import reverse_transform, writes
from pydantic import BaseModel


def generate_terragrunt_hcl_from_model(model: BaseModel, output_file_path: str) -> str:
    """
    Converts a Pydantic model instance representing a Terragrunt config into HCL2 and writes it to a file.

    This is intended to be used with schemas like `schemas.terragrunt_example.vpc`.

    Args:
        model (BaseModel): Pydantic model instance (e.g., `vpc`).
        output_file_path (str): The path to the output terragrunt.hcl file.

    Returns:
        str: The generated HCL content.
    """
    try:
        # Convert model to a plain dict (Pydantic v2: model_dump)
        json_data = model.model_dump()

        # Normalize the 'include' block to ensure the special path is used by default
        include_block = json_data.get("include")
        if isinstance(include_block, dict):
            include_block["path"] = "find_in_parent_folders()"
            json_data["include"] = include_block
        else:
            json_data["include"] = {"path": "find_in_parent_folders()"}

        # Convert dict to HCL2 AST and then to string
        hcl_ast = reverse_transform(json_data)
        hcl_content = writes(hcl_ast)

        with open(output_file_path, "w") as f:
            f.write(hcl_content)

        return hcl_content
    except Exception as e:
        # Surface the error to the caller (FastAPI will format it)
        raise e
