# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from pydantic import BaseModel


class ModuleInfo(BaseModel):
    name: str
    shortdesc: str
    description: str
    author: str
    is_custom: bool


class ModuleVersionInfo(BaseModel):
    version: str
    modules: list[ModuleInfo]


class ModuleInstalledInfo(BaseModel):
    # keep this for backward compatibility but it would be nice to remove this level
    # or deprecate it somehow
    modules_info: ModuleVersionInfo
