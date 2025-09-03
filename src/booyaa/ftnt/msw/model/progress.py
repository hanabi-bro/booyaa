from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

@dataclass
class Login:
    code: int = -999
    msg: str = ''
    output: str | bytes | dict | dict[str, Any] | list[Any] = ''

class Backup:
    code: int = -999
    msg: str = ''
    output: str | bytes | dict | dict[str, Any] | list[Any] = ''

class Logout:
    code: int = -999
    msg: str = ''
    output: str | bytes | dict | dict[str, Any] | list[Any] = ''

@dataclass
class Progress:
    login: Login = field(default_factory=Login)
    backup: Backup = field(default_factory=Backup)
    Logout: Logout = field(default_factory=Logout)
    msg: str = ''
