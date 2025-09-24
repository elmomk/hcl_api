# Terragrunt Automation API

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

A FastAPI service that accepts Terragrunt configuration as JSON (validated by Pydantic models) and generates a `terragrunt.hcl` file using the `hcl2` library.

## Features

- Validates requests with Pydantic models in `api/app/schemas/terragrunt_example.py`
- Converts JSON payloads to HCL2 via `hcl2.api.reverse_transform` in `api/app/library/json2hcl.py`
- REST endpoint to create a VPC Terragrunt config and write it to disk
- OpenAPI docs with examples for quick testing

## Project Structure

```
terragrunt_automation/
├─ api/
│  └─ app/
│     ├─ main.py                      # FastAPI app entrypoint
│     ├─ routers/
│     │  └─ config_creation.py        # /tf/vpc endpoint
│     ├─ library/
│     │  └─ json2hcl.py               # JSON→HCL conversion utilities
│     └─ schemas/
│        └─ terragrunt_example.py     # Pydantic models (Include, Terraform, Inputs, TerragruntModule, TerragruntConfig)
└─ README.md
```

## Requirements

- Python 3.11+
- pip packages:
  - fastapi
  - uvicorn
  - pydantic>=2
  - python-hcl2 (exposes `hcl2.api.reverse_transform` and `hcl2.api.writes`)

If you don’t have a `requirements.txt`, you can install:

```bash
pip install -r requirements.txt
# or
pip install "fastapi[standard]" python-hcl2
```

## Running the API

From the `api/app/` directory, start the server with Uvicorn:

```bash
fastapi dev main.py
```

- OpenAPI/Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Endpoint

- POST `/tf/vpc`
  - Body: `vpc` model (a wrapper including `conf_path` and a nested Terragrunt configuration)
  - Writes the generated `terragrunt.hcl` to `conf_path`
  - Returns the HCL content, file path, and echoed/validated payload

### Request Model (summarized)

Defined in `api/app/schemas/terragrunt_example.py`:

- `Include`
  - `path`: literal `"find_in_parent_folders()"` or `str` (defaults to the literal)
- `Terraform`
  - `source`: str (Git URL/local path; defaults to example VPC module)
- `Inputs`
  - `vpc_name`: str (default: `production-vpc`)
  - `vpc_cidr`: str (default: `10.0.0.0/16`)
  - `enable_dns_support`: bool (default: `true`)
  - `public_subnets`: list[str] (default example values via `default_factory`)
  - `tags`: dict[str, str] (default example values via `default_factory`)
- `TerragruntModule`
  - `include`: Include
  - `terraform`: Terraform
  - `inputs`: Inputs
- `vpc` (wrapper used by the endpoint)
  - `conf_path`: str (where to write `terragrunt.hcl`; default `/tmp/terragrunt_vpc.hcl`)
  - `terragrunt`: TerragruntModule

Note: The OpenAPI docs show examples for arrays/maps via `json_schema_extra`. `default_factory` values are applied at runtime, but do not appear as JSON Schema defaults.

### Example Request

Use the try-it-out in Swagger UI, or `curl`:

```bash
curl -X POST http://localhost:8000/tf/vpc \
  -H 'Content-Type: application/json' \
  -d '{
    "conf_path": "/tmp/terragrunt_vpc.hcl",
    "terragrunt": {
      "include": { "path": "find_in_parent_folders()" },
      "terraform": {
        "source": "git::git@github.com:my-org/terraform-modules.git//vpc?ref=v1.2.0"
      },
      "inputs": {
        "vpc_name": "production-vpc",
        "vpc_cidr": "10.0.0.0/16",
        "enable_dns_support": true,
        "public_subnets": [
          "10.0.1.0/24",
          "10.0.2.0/24"
        ],
        "tags": { "project": "web-app", "environment": "prod" }
      }
    }
  }'
```

### Example Response

```json
{
  "hcl_path": "/tmp/terragrunt_vpc.hcl",
  "hcl": "include {\n  path = \"find_in_parent_folders()\"\n}\n\nterraform {\n  source = \"git::git@github.com:my-org/terraform-modules.git//vpc?ref=v1.2.0\"\n}\n\ninputs = {\n  vpc_name = \"production-vpc\"\n  vpc_cidr = \"10.0.0.0/16\"\n  enable_dns_support = true\n  public_subnets = [\n    \"10.0.1.0/24\",\n    \"10.0.2.0/24\"\n  ]\n  tags = {\n    environment = \"prod\"\n    project = \"web-app\"\n  }\n}\n",
  "payload": { /* your validated request payload */ }
}
```

## How HCL Generation Works

- The endpoint passes the validated Pydantic model to `generate_terragrunt_hcl_from_model()` in `api/app/library/json2hcl.py`.
- The model is converted to a plain `dict` via `model_dump()` and normalized (e.g., enforcing `include.path = "find_in_parent_folders()"`).
- The dict is transformed to HCL2 AST with `reverse_transform()` and stringified with `writes()`.
- The HCL is written to `conf_path` and returned in the response.

## Notes & Tips

- This project targets Python 3.11 and Pydantic v2. Preferred typing style uses built-in generics (e.g., `list[str]`, `dict[str, str]`) and `T | None`.
- The `Literal` type highlights the special value `find_in_parent_folders()` for discoverability, while still allowing any path string.
- If you want schema defaults to appear in OpenAPI as actual defaults (not just examples), use static JSON-serializable defaults or add `json_schema_extra` examples (already added for arrays/maps).
- Consider adding CIDR and path validation (regex or custom validators) if needed.

## Development

- Format/lint with your preferred tools (e.g., ruff, black).
- Extend the models for other modules by following the `TerragruntModule` pattern.
- Add more routers under `api/app/routers/` for new endpoints.

## License

AGPL-3.0. In short: this is a strong copyleft license for networked software — if you modify and run this service over a network, you must make the complete corresponding source available to users of the service.

See the full text in `LICENSE` or read more at the [GNU AGPL v3 page](https://www.gnu.org/licenses/agpl-3.0).

### Copyright header template

Use this header in new source files to declare licensing information:

```text
Copyright (C) 2025

This file is part of Terragrunt Automation API.

Terragrunt Automation API is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Terragrunt Automation API is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with Terragrunt Automation API. If not, see <https://www.gnu.org/licenses/>.
```
