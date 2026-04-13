"""
智能模拟数据生成模块

生成比真的还真的数据：
- 角色模板系统（Persona Templates）
- 校园时间规律（Campus Rhythm）
- 资源冲突注入（Resource Conflicts）
- 脏数据污染（5% Dirty Data）
- 质量自验证（Quality Self-Check）
"""

from .personas import PersonaGenerator, StudentPersona
from .campus_rhythm import CampusRhythmGenerator
from .conflict_injector import ConflictInjector
from .dirty_data_injector import DirtyDataInjector
from .smart_data_generator import SmartDataGenerator

__all__ = [
    "PersonaGenerator",
    "StudentPersona",
    "CampusRhythmGenerator",
    "ConflictInjector",
    "DirtyDataInjector",
    "SmartDataGenerator",
]
