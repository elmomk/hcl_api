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


class Hook(BaseModel):
    """Hook to run before/after specific Terraform commands."""

    name: str = Field(description="Name of the hook.")
    commands: list[str] = Field(
        default_factory=list,
        description="Terraform commands that will trigger this hook (e.g., apply, plan, init).",
    )
    execute: list[str] = Field(
        default_factory=list,
        description="The command to execute as a list (argv-style).",
    )
    run_on_error: bool = Field(
        default=False,
        description="Whether to run this hook when a Terraform command errors.",
    )
    working_dir: str | None = Field(
        default=None,
        description="Optional working directory for the executed command.",
    )
    env_vars: dict[str, str] = Field(
        default_factory=dict,
        description="Environment variables for the executed command.",
    )


class ExtraArguments(BaseModel):
    """Additional CLI args/env for specific Terraform commands."""

    name: str = Field(description="Name of this argument set.")
    commands: list[str] = Field(
        default_factory=list,
        description="Terraform commands where these args apply (e.g., init, plan, apply).",
    )
    arguments: list[str] = Field(
        default_factory=list,
        description="Additional arguments to pass to Terraform for the given commands.",
    )
    optional_var_files: list[str] = Field(
        default_factory=list,
        description=(
            "List of -var-file paths to include if they exist (non-fatal if missing)."
        ),
    )
    env_vars: dict[str, str] = Field(
        default_factory=dict,
        description="Environment variables to set when running those commands.",
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
    include_in_copy: list[str] = Field(
        default_factory=list,
        description=(
            "Extra files/paths to include when copying the source module to Terragrunt's temp dir."
        ),
    )
    extra_arguments: list[ExtraArguments] = Field(
        default_factory=list,
        description="Extra CLI args and env vars to inject for specific commands.",
    )
    before_hook: list[Hook] = Field(
        default_factory=list,
        description="Hooks to run before specific Terraform commands.",
    )
    after_hook: list[Hook] = Field(
        default_factory=list,
        description="Hooks to run after specific Terraform commands.",
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
                            ),
                            "include_in_copy": [
                                "README.md",
                                "modules/common/variables.tf",
                            ],
                            "extra_arguments": [
                                {
                                    "name": "common-vars",
                                    "commands": ["plan", "apply"],
                                    "arguments": [
                                        "-lock-timeout=10m",
                                        "-parallelism=10",
                                    ],
                                    "optional_var_files": [
                                        "env/${TG_VAR_environment}.tfvars",
                                    ],
                                    "env_vars": {"TF_LOG": "WARN"},
                                }
                            ],
                            "before_hook": [
                                {
                                    "name": "fmt",
                                    "commands": ["plan", "apply"],
                                    "execute": ["tofu", "fmt", "-recursive"],
                                    "run_on_error": False,
                                }
                            ],
                            "after_hook": [
                                {
                                    "name": "notify",
                                    "commands": ["apply"],
                                    "execute": [
                                        "bash",
                                        "-lc",
                                        "echo 'Apply finished'",
                                    ],
                                    "run_on_error": False,
                                }
                            ],
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
