"""Pydantic schemas for Terragrunt configuration payloads.

This module defines nested models for Include, Terraform, Inputs, and wrapper
models for submitting Terragrunt configuration to the API.
"""
from typing import Literal
from pydantic import BaseModel, Field


class Include(BaseModel):
    """Terragrunt include block.

    Controls how this module inherits configuration from parent folders.

    Attributes:
        path (Literal["find_in_parent_folders()"] | str): Special value
            'find_in_parent_folders()' to auto-discover the parent terragrunt.hcl,
            or a string path to a specific parent directory/file.
    """

    path: Literal["find_in_parent_folders()"] | str = Field(
        default="find_in_parent_folders()",
        description=(
            "Special value 'find_in_parent_folders()' to auto-discover parent terragrunt.hcl, "
            "or a string path to a specific parent directory/file."
        ),
    )


class Terraform(BaseModel):
    """Terraform source configuration for this module."""

    source: str = Field(
        default=(
            "git::git@github.com:my-org/terraform-modules.git//vpc?ref=v1.2.0"
        ),
        description=(
            "Module source URL. Supports Git URLs (e.g., git::https://..., ssh), "
            "local paths, and ref query for version pinning (e.g., ?ref=v1.2.0)."
        ),
    )


class Inputs(BaseModel):
    """Inputs passed to the Terraform module via Terragrunt."""

    vpc_name: str = Field(
        default="production-vpc",
        description="Human-readable name for the VPC.",
    )
    vpc_cidr: str = Field(
        default="10.0.0.0/16",
        description="CIDR block for the VPC, e.g. 10.0.0.0/16.",
    )
    enable_dns_support: bool = Field(
        default=True,
        description="Whether to enable DNS resolution in the VPC.",
    )
    public_subnets: list[str] = Field(
        default_factory=lambda: ["10.0.1.0/24", "10.0.2.0/24"],
        description="List of CIDR blocks for public subnets.",
        json_schema_extra={"examples": [["10.0.1.0/24", "10.0.2.0/24"]]},
    )
    tags: dict[str, str] = Field(
        default_factory=lambda: {"project": "web-app", "environment": "prod"},
        description="Key/value tags applied to created resources.",
        json_schema_extra={"examples": [{"project": "web-app", "environment": "prod"}]},
    )


class TerragruntConfig(BaseModel):
    """Top-level Terragrunt configuration model matching the example JSON structure."""

    include: Include = Field(
        default_factory=Include, description="Terragrunt include block."
    )
    terraform: Terraform = Field(
        default_factory=Terraform, description="Terraform source configuration."
    )
    inputs: Inputs = Field(
        default_factory=Inputs, description="Inputs forwarded to the Terraform module."
    )


class VPC(BaseModel):
    """Wrapper config including output path and the Terragrunt module."""

    conf_path: str = Field(
        default="/tmp/terragrunt_vpc.hcl",
        description="Path where the generated terragrunt.hcl should be written.",
    )
    terragrunt: TerragruntConfig = Field(
        default_factory=TerragruntConfig,
        description="The Terragrunt module configuration.",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "conf_path": "/tmp/terragrunt_vpc.hcl",
                    "terragrunt": {
                        "include": {"path": "find_in_parent_folders()"},
                        "terraform": {
                            "source": (
                                "git::git@github.com:my-org/terraform-modules.git//vpc"
                                "?ref=v1.2.0"
                            )
                        },
                        "inputs": {
                            "vpc_name": "production-vpc",
                            "vpc_cidr": "10.0.0.0/16",
                            "enable_dns_support": True,
                            "public_subnets": [
                                "10.0.1.0/24",
                                "10.0.2.0/24",
                            ],
                            "tags": {"project": "web-app", "environment": "prod"},
                        },
                    },
                }
            ]
        }
    }
