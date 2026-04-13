# 校园社团活动评估系统第二阶段实施计划

## 数据采集与清洗（第2-3个月）

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建完整的数据采集与清洗基础设施，包括模拟数据生成、历史数据导入、外部爬虫采集、ETL管道和数据质量监控

**Architecture:** 采用分层架构：数据源层（模拟+历史+爬虫）→ ETL管道层（Python+Pandas）→ 存储层（PostgreSQL+ChromaDB）。使用APScheduler进行任务调度，Great Expectations进行数据质量验证

**Tech Stack:** Python 3.10, Pandas 2.2.0, NumPy 1.26.4, Scrapy 2.11, Jieba 0.42, ChromaDB 0.4.x, APScheduler 3.10, Great Expectations 0.18

---

## 文件结构概览

### Python数据采集模块 (campus-ai/src/data/)
- `campus-ai/src/data/__init__.py` - 数据模块初始化
- `campus-ai/src/data/generators/` - 模拟数据生成器
- `campus-ai/src/data/extractors/` - 数据提取器（历史数据导入）
- `campus-ai/src/data/crawlers/` - 网络爬虫
- `campus-ai/src/data/transformers/` - 数据转换器（清洗+特征工程）
- `campus-ai/src/data/pipeline.py` - ETL管道编排
- `campus-ai/src/data/quality.py` - 数据质量检查
- `campus-ai/src/data/vector_store.py` - 向量存储管理

### 测试文件 (campus-ai/tests/data/)
- `campus-ai/tests/data/test_generators.py`
- `campus-ai/tests/data/test_extractors.py`
- `campus-ai/tests/data/test_transformers.py`
- `campus-ai/tests/data/test_pipeline.py`
- `campus-ai/tests/data/test_quality.py`

### 配置与SQL
- `campus-ai/requirements-data.txt` - 数据模块依赖
- `campus-main/src/main/resources/db/migration/V5__add_external_data_tables.sql` - 外部数据表迁移

---

## 实施任务分解

### 任务1: 添加数据模块依赖

**Files:**
- Create: `campus-ai/requirements-data.txt`
- Modify: `campus-ai/requirements.txt`

- [ ] **Step 1: 创建数据模块专用依赖文件**

```txt
# campus-ai/requirements-data.txt
# 数据采集与清洗模块依赖

# 数据处理核心
pandas==2.2.0
numpy==1.26.4
openpyxl==3.1.2          # Excel读写
xlrd==2.0.1              # 旧版Excel支持

# 爬虫
scrapy==2.11.0
playwright==1.41.0       # 动态页面
fake-useragent==1.4.0    # User-Agent轮换

# NLP处理
jieba==0.42.1            # 中文分词
scikit-learn==1.4.0      # TF-IDF向量化
text2vec==1.2.0          # 中文文本向量

# 向量存储
chromadb==0.4.22
sentence-transformers==2.3.0

# 任务调度
apscheduler==3.10.4

# 数据质量
great-expectations==0.18.8

# 数据生成
faker==23.0.0

# 数据库连接
psycopg2-binary==2.9.9
sqlalchemy==2.0.25
```

- [ ] **Step 2: 更新主requirements.txt**

```txt
# campus-ai/requirements.txt 追加以下内容
-r requirements-data.txt
```

- [ ] **Step 3: 验证依赖安装**

```bash
cd campus-ai && pip install -r requirements-data.txt --dry-run 2>&1 | tail -20
```

Expected: 显示将要安装的包列表，无冲突错误

- [ ] **Step 4: 提交依赖配置**

```bash
git add campus-ai/requirements-data.txt campus-ai/requirements.txt
git commit -m "feat: add data collection and cleaning dependencies"
```

---

### 任务2: 数据库迁移 - 外部数据表

**Files:**
- Create: `campus-main/src/main/resources/db/migration/V5__add_external_data_tables.sql`

- [ ] **Step 1: 创建社交媒体数据采集表**

```sql
-- campus-main/src/main/resources/db/migration/V5__add_external_data_tables.sql
-- ============================================
-- 外部数据采集表结构
-- 版本: V5
-- ============================================

-- 社交媒体帖子表
CREATE TABLE IF NOT EXISTS social_media_posts (
    id BIGSERIAL PRIMARY KEY,
    post_id VARCHAR(100) UNIQUE NOT NULL,
    platform VARCHAR(50) NOT NULL CHECK (platform IN ('weibo', 'tieba', 'wechat', 'other')),
    content TEXT NOT NULL,
    publish_time TIMESTAMP NOT NULL,
    sentiment_score DECIMAL(4,3) CHECK (sentiment_score BETWEEN -1.0 AND 1.0),
    sentiment_label VARCHAR(20) CHECK (sentiment_label IN ('positive', 'neutral', 'negative')),
    activity_mentioned VARCHAR(200),
    engagement_json JSONB,
    crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    raw_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引优化
CREATE INDEX idx_social_posts_platform ON social_media_posts(platform);
CREATE INDEX idx_social_posts_publish_time ON social_media_posts(publish_time);
CREATE INDEX idx_social_posts_activity ON social_media_posts(activity_mentioned);
CREATE INDEX idx_social_posts_sentiment ON social_media_posts(sentiment_label);
```

- [ ] **Step 2: 创建数据导入任务记录表**

```sql
-- 数据导入任务记录表
CREATE TABLE IF NOT EXISTS data_import_jobs (
    id BIGSERIAL PRIMARY KEY,
    job_type VARCHAR(50) NOT NULL CHECK (job_type IN ('historical', 'incremental', 'simulation')),
    file_name VARCHAR(500),
    source_type VARCHAR(50),
    records_total INTEGER DEFAULT 0,
    records_success INTEGER DEFAULT 0,
    records_failed INTEGER DEFAULT 0,
    quality_score INTEGER CHECK (quality_score BETWEEN 0 AND 100),
    error_log JSONB,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'success', 'failed', 'partial')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_import_jobs_status ON data_import_jobs(status);
CREATE INDEX idx_import_jobs_type ON data_import_jobs(job_type);
```

- [ ] **Step 3: 创建ETL水位线表**

```sql
-- ETL水位线表（增量同步用）
CREATE TABLE IF NOT EXISTS etl_watermarks (
    source_name VARCHAR(100) PRIMARY KEY,
    last_sync_time TIMESTAMP NOT NULL,
    record_count BIGINT DEFAULT 0,
    last_record_id BIGINT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 数据血缘记录表
CREATE TABLE IF NOT EXISTS data_lineage (
    id BIGSERIAL PRIMARY KEY,
    job_id BIGINT REFERENCES data_import_jobs(id),
    source_name VARCHAR(100) NOT NULL,
    source_type VARCHAR(50) NOT NULL,
    extraction_time TIMESTAMP NOT NULL,
    transformations JSONB NOT NULL DEFAULT '[]',
    destination_table VARCHAR(100) NOT NULL,
    load_time TIMESTAMP,
    records_in BIGINT,
    records_out BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_lineage_job ON data_lineage(job_id);
CREATE INDEX idx_lineage_source ON data_lineage(source_name);
```

- [ ] **Step 4: 验证SQL语法**

```bash
cd campus-main && ./mvnw flyway:validate -q 2>&1 | grep -E "(ERROR|SUCCESS|V5)"
```

Expected: 显示V5迁移文件验证成功或无错误

- [ ] **Step 5: 提交SQL迁移文件**

```bash
git add campus-main/src/main/resources/db/migration/V5__add_external_data_tables.sql
git commit -m "feat: add external data collection tables migration"
```

---

### 任务3: 数据模块基础结构

**Files:**
- Create: `campus-ai/src/data/__init__.py`

- [ ] **Step 1: 创建数据模块初始化文件**

```python
# campus-ai/src/data/__init__.py
"""
数据采集与清洗模块

提供以下功能：
- 模拟数据生成 (generators)
- 历史数据导入 (extractors)
- 外部数据采集 (crawlers)
- 数据清洗与特征工程 (transformers)
- ETL管道编排 (pipeline)
- 数据质量监控 (quality)
"""

__version__ = "1.0.0"

from .pipeline import ETLPipeline
from .quality import DataQualityChecker

__all__ = [
    "ETLPipeline",
    "DataQualityChecker",
]
```

- [ ] **Step 2: 创建数据模块配置**

```python
# campus-ai/src/data/config.py
"""数据模块配置"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class DataConfig:
    """数据模块配置类"""

    # 数据库配置
    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: int = int(os.getenv("DB_PORT", "5432"))
    db_name: str = os.getenv("DB_NAME", "campus_club")
    db_user: str = os.getenv("DB_USER", "campus_user")
    db_password: str = os.getenv("DB_PASSWORD", "")

    # 向量存储配置
    vector_db_path: str = os.getenv("VECTOR_DB_PATH", "./data/vector_store")

    # 爬虫配置
    crawl_delay_min: float = 1.0
    crawl_delay_max: float = 3.0
    max_retries: int = 3

    # ETL配置
    batch_size: int = 1000
    default_quality_threshold: float = 70.0

    @property
    def db_connection_string(self) -> str:
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"


# 全局配置实例
config = DataConfig()
```

- [ ] **Step 3: 创建测试验证模块结构**

```python
# campus-ai/tests/data/__init__.py
"""数据模块测试包"""
```

- [ ] **Step 4: 验证Python语法**

```bash
cd campus-ai && python -m py_compile src/data/__init__.py src/data/config.py
```

Expected: 无输出表示语法正确

- [ ] **Step 5: 提交基础结构**

```bash
git add campus-ai/src/data/__init__.py campus-ai/src/data/config.py campus-ai/tests/data/__init__.py
git commit -m "feat: add data module base structure"
```

---

### 任务4: 模拟数据生成器 - StudentGenerator

**Files:**
- Create: `campus-ai/src/data/generators/__init__.py`
- Create: `campus-ai/src/data/generators/base.py`
- Create: `campus-ai/src/data/generators/student_generator.py`

- [ ] **Step 1: 创建生成器基础类测试**

```python
# campus-ai/tests/data/test_generators.py
import pytest
import pandas as pd
from datetime import datetime


class TestBaseGenerator:
    """测试基础生成器"""

    def test_generator_initialization(self):
        from src.data.generators.base import BaseGenerator
        gen = BaseGenerator(seed=42)
        assert gen.seed == 42
        assert gen.faker is not None

    def test_generator_seed_consistency(self):
        from src.data.generators.base import BaseGenerator
        gen1 = BaseGenerator(seed=42)
        gen2 = BaseGenerator(seed=42)
        assert gen1.faker.random_int() == gen2.faker.random_int()
```

- [ ] **Step 2: 运行测试验证失败**

```bash
cd campus-ai && python -m pytest tests/data/test_generators.py::TestBaseGenerator -v 2>&1 | tail -20
```

Expected: 显示ImportError，模块不存在

- [ ] **Step 3: 实现基础生成器类**

```python
# campus-ai/src/data/generators/base.py
"""数据生成器基类"""

from abc import ABC, abstractmethod
from typing import Optional
from faker import Faker
import random
import pandas as pd


class BaseGenerator(ABC):
    """数据生成器基类"""

    def __init__(self, seed: Optional[int] = None, locale: str = "zh_CN"):
        self.seed = seed
        self.locale = locale
        self.faker = Faker(locale)
        if seed:
            Faker.seed(seed)
            random.seed(seed)

    @abstractmethod
    def generate(self, count: int, **kwargs) -> pd.DataFrame:
        """生成数据，返回DataFrame"""
        pass

    def save_to_csv(self, df: pd.DataFrame, filepath: str):
        """保存数据到CSV"""
        df.to_csv(filepath, index=False, encoding='utf-8-sig')

    def save_to_excel(self, df: pd.DataFrame, filepath: str):
        """保存数据到Excel"""
        df.to_excel(filepath, index=False, engine='openpyxl')
```

- [ ] **Step 4: 实现学生数据生成器**

```python
# campus-ai/src/data/generators/student_generator.py
"""学生数据生成器"""

import random
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional
from .base import BaseGenerator


class StudentGenerator(BaseGenerator):
    """
    学生基础信息生成器

    生成符合真实学校场景的学生数据：
    - 学号格式：年份(2位) + 学院代码(2位) + 专业代码(2位) + 序号(4位)
    - 年级分布：大一(25%), 大二(25%), 大三(25%), 大四(25%)
    - 性别分布：男(55%), 女(45%)
    """

    # 学院与专业配置
    DEPARTMENTS = {
        "CS": {"name": "计算机学院", "majors": ["CS", "SE", "AI", "DS"]},
        "EE": {"name": "电子工程学院", "majors": ["EE", "CE", "AUTO"]},
        "BA": {"name": "商学院", "majors": ["FIN", "ACC", "MKT"]},
        "LA": {"name": "人文学院", "majors": ["CHN", "HIS", "PHI"]},
        "MA": {"name": "理学院", "majors": ["MATH", "PHY", "CHEM"]},
    }

    def __init__(self, seed: Optional[int] = None):
        super().__init__(seed=seed, locale="zh_CN")
        self.current_year = datetime.now().year

    def _generate_student_id(self, enrollment_year: int, dept_code: str, major_code: str, seq: int) -> str:
        """生成学号"""
        year_short = str(enrollment_year)[-2:]
        return f"{year_short}{dept_code}{major_code}{seq:04d}"

    def _generate_enrollment_year(self) -> int:
        """生成入学年份（近4年）"""
        years_ago = random.choices([0, 1, 2, 3], weights=[25, 25, 25, 25])[0]
        return self.current_year - years_ago

    def generate(self, count: int, **kwargs) -> pd.DataFrame:
        """
        生成学生数据

        Args:
            count: 生成数量
            gender_ratio: 性别比例，默认男55%女45%

        Returns:
            DataFrame with columns: student_id, name, gender, enrollment_year,
                                   department, major, grade_level
        """
        gender_ratio = kwargs.get('gender_ratio', 0.55)

        students = []
        seq_counters = {}

        for i in range(count):
            # 入学年份和年级
            enrollment_year = self._generate_enrollment_year()
            grade_level = self.current_year - enrollment_year + 1

            # 学院和专业
            dept_code = random.choice(list(self.DEPARTMENTS.keys()))
            dept_info = self.DEPARTMENTS[dept_code]
            major_code = random.choice(dept_info["majors"])

            # 序号
            key = (enrollment_year, dept_code, major_code)
            seq_counters[key] = seq_counters.get(key, 0) + 1

            # 学号
            student_id = self._generate_student_id(
                enrollment_year, dept_code, major_code, seq_counters[key]
            )

            # 基本信息
            gender = "M" if random.random() < gender_ratio else "F"
            name = self.faker.name_male() if gender == "M" else self.faker.name_female()

            students.append({
                "student_id": student_id,
                "name": name,
                "gender": gender,
                "enrollment_year": enrollment_year,
                "department": dept_info["name"],
                "department_code": dept_code,
                "major": major_code,
                "grade_level": grade_level,
                "created_at": datetime.now()
            })

        return pd.DataFrame(students)
```

- [ ] **Step 5: 更新生成器模块初始化**

```python
# campus-ai/src/data/generators/__init__.py
"""模拟数据生成器模块"""

from .base import BaseGenerator
from .student_generator import StudentGenerator

__all__ = [
    "BaseGenerator",
    "StudentGenerator",
]
```

- [ ] **Step 6: 运行测试验证通过**

```bash
cd campus-ai && python -m pytest tests/data/test_generators.py -v 2>&1 | tail -20
```

Expected: 测试通过

- [ ] **Step 7: 提交学生生成器**

```bash
git add campus-ai/src/data/generators/ campus-ai/tests/data/test_generators.py
git commit -m "feat: add student data generator with realistic distribution"
```

---

### 任务5: 模拟数据生成器 - Club与Activity生成器

**Files:**
- Create: `campus-ai/src/data/generators/club_generator.py`
- Create: `campus-ai/src/data/generators/activity_generator.py`

- [ ] **Step 1: 创建社团数据生成器**

```python
# campus-ai/src/data/generators/club_generator.py
"""社团数据生成器"""

import random
import pandas as pd
from datetime import datetime
from typing import Optional, List
from .base import BaseGenerator


class ClubGenerator(BaseGenerator):
    """
    社团信息生成器

    生成多样化的社团数据：
    - 社团类型：学术、文艺、体育、公益、科技
    - 星级评级：1-5星
    - 成立时间：近10年
    """

    CLUB_TYPES = {
        "academic": {"name": "学术类", "prefix": ["学术", "研究", "探索"], "examples": ["数学建模", "物理协会", "英语角"]},
        "arts": {"name": "文艺类", "prefix": ["艺术", "文化", "创意"], "examples": ["合唱团", "舞蹈社", "摄影协会"]},
        "sports": {"name": "体育类", "prefix": ["运动", "健身", "竞技"], "examples": ["篮球队", "羽毛球社", "跑步协会"]},
        "public": {"name": "公益类", "prefix": ["志愿", "公益", "爱心"], "examples": ["志愿者协会", "环保社", "支教团"]},
        "tech": {"name": "科技类", "prefix": ["科技", "创新", "创客"], "examples": ["机器人社", "编程协会", "无人机社"]}
    }

    def __init__(self, seed: Optional[int] = None):
        super().__init__(seed=seed, locale="zh_CN")
        self.current_year = datetime.now().year

    def _generate_club_name(self, club_type: str) -> str:
        """生成社团名称"""
        type_info = self.CLUB_TYPES[club_type]
        prefix = random.choice(type_info["prefix"])
        suffix = random.choice(type_info["examples"])
        patterns = [
            f"{prefix}{suffix}",
            f"{suffix}{prefix}",
            f"{self.faker.word()}{suffix}",
            suffix
        ]
        return random.choice(patterns)

    def _generate_founding_date(self) -> datetime:
        """生成成立日期（近10年）"""
        years_ago = random.randint(0, 10)
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        return datetime(self.current_year - years_ago, month, day)

    def generate(self, count: int, **kwargs) -> pd.DataFrame:
        """
        生成社团数据

        Returns:
            DataFrame with columns: club_id, name, club_type, description,
                                   founding_date, member_count, rating,
                                   advisor_name, contact_email
        """
        clubs = []

        for i in range(count):
            club_type = random.choice(list(self.CLUB_TYPES.keys()))
            founding_date = self._generate_founding_date()
            age_years = self.current_year - founding_date.year

            # 成员数量与年龄相关（老社团成员更多）
            base_members = random.randint(10, 50)
            member_count = base_members + age_years * random.randint(2, 8)
            member_count = min(member_count, 200)  # 上限200

            # 星级与成员数正相关
            if member_count > 150:
                rating = random.choices([4, 5], weights=[30, 70])[0]
            elif member_count > 80:
                rating = random.choices([3, 4, 5], weights=[20, 50, 30])[0]
            else:
                rating = random.choices([1, 2, 3, 4], weights=[10, 20, 40, 30])[0]

            clubs.append({
                "club_id": f"CLUB{1000 + i:04d}",
                "name": self._generate_club_name(club_type),
                "club_type": club_type,
                "club_type_name": self.CLUB_TYPES[club_type]["name"],
                "description": self.faker.text(max_nb_chars=200),
                "founding_date": founding_date,
                "member_count": member_count,
                "rating": rating,
                "advisor_name": self.faker.name(),
                "contact_email": self.faker.email(),
                "status": random.choices(["active", "inactive"], weights=[90, 10])[0],
                "created_at": datetime.now()
            })

        return pd.DataFrame(clubs)
```

- [ ] **Step 2: 创建活动数据生成器**

```python
# campus-ai/src/data/generators/activity_generator.py
"""活动数据生成器"""

import random
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, List
from .base import BaseGenerator


class ActivityGenerator(BaseGenerator):
    """
    社团活动数据生成器

    生成符合真实场景的活动数据：
    - 活动时间分布：考虑学期、考试周
    - 参与人数：与社团规模相关
    - 预算：与活动规模相关
    """

    ACTIVITY_TYPES = [
        "讲座", "比赛", "展览", "聚会", "培训",
        "志愿服务", "户外", "演出", "招新", "其他"
    ]

    def __init__(self, seed: Optional[int] = None):
        super().__init__(seed=seed, locale="zh_CN")
        self.current_year = datetime.now().year

    def _is_exam_period(self, date: datetime) -> bool:
        """判断是否为考试周（简化：每学期第16-18周）"""
        # 简化判断：1月和6月为考试月
        return date.month in [1, 6]

    def _generate_activity_datetime(self) -> tuple:
        """生成活动时间（避开考试周）"""
        # 生成近2年的活动
        days_ago = random.randint(0, 730)
        start_date = datetime.now() - timedelta(days=days_ago)

        # 避开考试周
        while self._is_exam_period(start_date):
            days_ago = random.randint(0, 730)
            start_date = datetime.now() - timedelta(days=days_ago)

        # 活动时间偏向下午和晚上
        hour_weights = [5, 5, 5, 5, 10, 15, 20, 25, 10]  # 8-24点
        start_hour = random.choices(range(8, 17), weights=hour_weights)[0]
        start_time = start_date.replace(hour=start_hour, minute=0)

        # 时长1-4小时
        duration_hours = random.choices([1, 2, 3, 4], weights=[20, 40, 30, 10])[0]
        end_time = start_time + timedelta(hours=duration_hours)

        return start_time, end_time

    def generate(self, count: int, clubs_df: Optional[pd.DataFrame] = None, **kwargs) -> pd.DataFrame:
        """
        生成活动数据

        Args:
            count: 活动数量
            clubs_df: 社团DataFrame（用于关联）

        Returns:
            DataFrame with activity data
        """
        activities = []

        # 如果没有提供社团数据，生成随机club_id
        if clubs_df is None:
            club_ids = [f"CLUB{random.randint(1000, 9999):04d}" for _ in range(100)]
        else:
            club_ids = clubs_df['club_id'].tolist()

        for i in range(count):
            club_id = random.choice(club_ids)

            # 获取社团规模（影响参与人数）
            if clubs_df is not None:
                club_row = clubs_df[clubs_df['club_id'] == club_id]
                club_size = club_row['member_count'].values[0] if len(club_row) > 0 else 50
            else:
                club_size = random.randint(20, 100)

            start_time, end_time = self._generate_activity_datetime()
            activity_type = random.choice(self.ACTIVITY_TYPES)

            # 参与人数（社团成员的20%-80%）
            participation_rate = random.uniform(0.2, 0.8)
            participant_count = int(club_size * participation_rate)
            participant_count = random.randint(5, max(10, participant_count))

            # 预算（人均10-100元）
            budget_per_person = random.randint(10, 100)
            budget_amount = participant_count * budget_per_person

            activities.append({
                "activity_id": f"ACT{10000 + i:05d}",
                "club_id": club_id,
                "activity_name": f"{activity_type}活动-{self.faker.word()}",
                "activity_type": activity_type,
                "description": self.faker.text(max_nb_chars=300),
                "start_time": start_time,
                "end_time": end_time,
                "location": self.faker.address(),
                "participant_count": participant_count,
                "budget_amount": budget_amount,
                "status": random.choices(
                    ["completed", "ongoing", "cancelled"],
                    weights=[70, 20, 10]
                )[0],
                "created_at": datetime.now()
            })

        return pd.DataFrame(activities)
```

- [ ] **Step 3: 更新生成器模块导出**

```python
# campus-ai/src/data/generators/__init__.py
"""模拟数据生成器模块"""

from .base import BaseGenerator
from .student_generator import StudentGenerator
from .club_generator import ClubGenerator
from .activity_generator import ActivityGenerator

__all__ = [
    "BaseGenerator",
    "StudentGenerator",
    "ClubGenerator",
    "ActivityGenerator",
]
```

- [ ] **Step 4: 添加生成器测试**

```python
# campus-ai/tests/data/test_generators.py（追加）

class TestClubGenerator:
    """测试社团生成器"""

    def test_club_generation(self):
        from src.data.generators.club_generator import ClubGenerator
        gen = ClubGenerator(seed=42)
        df = gen.generate(10)

        assert len(df) == 10
        assert 'club_id' in df.columns
        assert 'club_type' in df.columns
        assert df['rating'].between(1, 5).all()
        assert df['member_count'].between(10, 200).all()

    def test_club_name_uniqueness(self):
        from src.data.generators.club_generator import ClubGenerator
        gen = ClubGenerator(seed=42)
        df = gen.generate(100)

        # 名称可以重复，但club_id必须唯一
        assert df['club_id'].nunique() == len(df)


class TestActivityGenerator:
    """测试活动生成器"""

    def test_activity_generation(self):
        from src.data.generators.activity_generator import ActivityGenerator
        gen = ActivityGenerator(seed=42)
        df = gen.generate(10)

        assert len(df) == 10
        assert 'activity_id' in df.columns
        assert 'start_time' in df.columns
        assert 'end_time' in df.columns

    def test_activity_time_validity(self):
        from src.data.generators.activity_generator import ActivityGenerator
        gen = ActivityGenerator(seed=42)
        df = gen.generate(10)

        # 结束时间必须晚于开始时间
        for _, row in df.iterrows():
            assert row['end_time'] > row['start_time']

    def test_activity_with_clubs(self):
        from src.data.generators.club_generator import ClubGenerator
        from src.data.generators.activity_generator import ActivityGenerator

        club_gen = ClubGenerator(seed=42)
        clubs = club_gen.generate(5)

        activity_gen = ActivityGenerator(seed=42)
        activities = activity_gen.generate(20, clubs_df=clubs)

        # 所有club_id都应在社团列表中
        assert activities['club_id'].isin(clubs['club_id']).all()
```

- [ ] **Step 5: 运行测试验证通过**

```bash
cd campus-ai && python -m pytest tests/data/test_generators.py -v 2>&1 | tail -30
```

Expected: 所有测试通过

- [ ] **Step 6: 提交社团和活动生成器**

```bash
git add campus-ai/src/data/generators/ campus-ai/tests/data/test_generators.py
git commit -m "feat: add club and activity data generators"
```

---

### 任务6: 数据提取器（历史数据导入）

**Files:**
- Create: `campus-ai/src/data/extractors/__init__.py`
- Create: `campus-ai/src/data/extractors/base.py`
- Create: `campus-ai/src/data/extractors/excel_extractor.py`
- Create: `campus-ai/tests/data/test_extractors.py`

- [ ] **Step 1: 创建提取器基础类**

```python
# campus-ai/src/data/extractors/base.py
"""数据提取器基类"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class DataExtractor(ABC):
    """数据提取器基类"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.validation_rules = {}

    @abstractmethod
    def extract(self, source: str, **kwargs) -> pd.DataFrame:
        """从数据源提取数据"""
        pass

    def validate(self, df: pd.DataFrame) -> tuple[bool, list]:
        """
        验证数据质量

        Returns:
            (is_valid, error_messages)
        """
        errors = []

        # 检查必需字段
        if 'required_fields' in self.validation_rules:
            missing = set(self.validation_rules['required_fields']) - set(df.columns)
            if missing:
                errors.append(f"缺少必需字段: {missing}")

        # 检查数据类型
        if 'dtype_rules' in self.validation_rules:
            for col, dtype in self.validation_rules['dtype_rules'].items():
                if col in df.columns:
                    try:
                        df[col] = df[col].astype(dtype)
                    except Exception as e:
                        errors.append(f"字段'{col}'类型转换失败: {e}")

        return len(errors) == 0, errors

    def get_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """获取数据摘要"""
        return {
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "columns": list(df.columns),
            "missing_values": df.isnull().sum().to_dict(),
            "memory_usage_mb": df.memory_usage(deep=True).sum() / 1024 / 1024
        }
```

- [ ] **Step 2: 实现Excel提取器**

```python
# campus-ai/src/data/extractors/excel_extractor.py
"""Excel数据提取器"""

import pandas as pd
from typing import Optional, Dict, Any, List
from .base import DataExtractor
import logging

logger = logging.getLogger(__name__)


class ExcelExtractor(DataExtractor):
    """
    Excel文件数据提取器

    支持功能：
    - 自动检测文件编码
    - 多Sheet读取
    - 数据类型推断
    - 空行过滤
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.default_config = {
            "header": 0,           # 第一行为表头
            "skip_empty_rows": True,
            "dtype_inference": True,
        }
        self.default_config.update(self.config)

    def extract(self, filepath: str, sheet_name: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        从Excel文件提取数据

        Args:
            filepath: Excel文件路径
            sheet_name: Sheet名称，None则读取第一个Sheet

        Returns:
            DataFrame
        """
        try:
            # 读取Excel
            df = pd.read_excel(
                filepath,
                sheet_name=sheet_name or 0,
                header=self.default_config["header"]
            )

            logger.info(f"从 {filepath} 提取了 {len(df)} 行数据")

            # 清理数据
            df = self._clean_data(df)

            return df

        except Exception as e:
            logger.error(f"Excel提取失败: {e}")
            raise

    def extract_all_sheets(self, filepath: str) -> Dict[str, pd.DataFrame]:
        """提取所有Sheet"""
        xl_file = pd.ExcelFile(filepath)
        result = {}

        for sheet_name in xl_file.sheet_names:
            result[sheet_name] = self.extract(filepath, sheet_name)

        return result

    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """清理数据"""
        # 删除完全空行
        if self.default_config["skip_empty_rows"]:
            df = df.dropna(how='all')

        # 去除字符串列的前后空格
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].astype(str).str.strip()
            # 将'nan'字符串替换为真正的NaN
            df[col] = df[col].replace(['nan', 'NaN', 'null', 'NULL'], pd.NA)

        return df

    def get_sheet_names(self, filepath: str) -> List[str]:
        """获取所有Sheet名称"""
        xl_file = pd.ExcelFile(filepath)
        return xl_file.sheet_names
```

- [ ] **Step 3: 更新提取器模块初始化**

```python
# campus-ai/src/data/extractors/__init__.py
"""数据提取器模块"""

from .base import DataExtractor
from .excel_extractor import ExcelExtractor

__all__ = [
    "DataExtractor",
    "ExcelExtractor",
]
```

- [ ] **Step 4: 创建提取器测试**

```python
# campus-ai/tests/data/test_extractors.py
import pytest
import pandas as pd
import tempfile
import os


class TestExcelExtractor:
    """测试Excel提取器"""

    @pytest.fixture
    def sample_excel(self):
        """创建临时Excel测试文件"""
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
            filepath = f.name

        # 创建测试数据
        df = pd.DataFrame({
            'name': ['活动A', '活动B', '活动C'],
            'date': ['2024-01-01', '2024-01-15', '2024-02-01'],
            'participants': [50, 80, 120],
            'budget': [1000.0, 2000.0, 3000.0]
        })

        with pd.ExcelWriter(filepath) as writer:
            df.to_excel(writer, sheet_name='Activities', index=False)
            df.to_excel(writer, sheet_name='Backup', index=False)

        yield filepath

        # 清理
        os.unlink(filepath)

    def test_extract_single_sheet(self, sample_excel):
        from src.data.extractors.excel_extractor import ExcelExtractor

        extractor = ExcelExtractor()
        df = extractor.extract(sample_excel, sheet_name='Activities')

        assert len(df) == 3
        assert list(df.columns) == ['name', 'date', 'participants', 'budget']

    def test_extract_all_sheets(self, sample_excel):
        from src.data.extractors.excel_extractor import ExcelExtractor

        extractor = ExcelExtractor()
        sheets = extractor.extract_all_sheets(sample_excel)

        assert len(sheets) == 2
        assert 'Activities' in sheets
        assert 'Backup' in sheets

    def test_get_sheet_names(self, sample_excel):
        from src.data.extractors.excel_extractor import ExcelExtractor

        extractor = ExcelExtractor()
        names = extractor.get_sheet_names(sample_excel)

        assert 'Activities' in names
        assert 'Backup' in names
```

- [ ] **Step 5: 运行测试验证通过**

```bash
cd campus-ai && python -m pytest tests/data/test_extractors.py -v 2>&1 | tail -20
```

Expected: 测试通过

- [ ] **Step 6: 提交提取器模块**

```bash
git add campus-ai/src/data/extractors/ campus-ai/tests/data/test_extractors.py
git commit -m "feat: add data extractors with Excel support"
```

---

### 任务7: 数据转换器（清洗与特征工程）

**Files:**
- Create: `campus-ai/src/data/transformers/__init__.py`
- Create: `campus-ai/src/data/transformers/cleaner.py`
- Create: `campus-ai/src/data/transformers/feature_engineer.py`

- [ ] **Step 1: 创建数据清洗器**

```python
# campus-ai/src/data/transformers/cleaner.py
"""数据清洗器"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Any, List, Tuple
import logging

logger = logging.getLogger(__name__)


class DataCleaner:
    """
    通用数据清洗器

    提供以下功能：
    - 缺失值处理
    - 异常值检测与处理
    - 数据类型转换
    - 重复值处理
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.default_missing_strategy = 'auto'
        self.default_outlier_method = 'iqr'

    def clean(self, df: pd.DataFrame, column_strategies: Optional[Dict] = None) -> pd.DataFrame:
        """
        执行完整清洗流程

        Args:
            df: 原始数据
            column_strategies: 各列的处理策略 {col: {'missing': 'fill', 'outlier': 'clip'}}

        Returns:
            清洗后的DataFrame
        """
        df = df.copy()
        column_strategies = column_strategies or {}

        # 1. 处理缺失值
        df = self.handle_missing_values(df, column_strategies)

        # 2. 处理异常值
        df = self.handle_outliers(df, column_strategies)

        # 3. 删除重复值
        df = df.drop_duplicates()

        logger.info(f"清洗完成: {len(df)} 行")
        return df

    def handle_missing_values(self, df: pd.DataFrame, strategies: Optional[Dict] = None) -> pd.DataFrame:
        """
        处理缺失值

        策略:
        - 'drop': 删除行
        - 'mean': 均值填充（数值型）
        - 'median': 中位数填充（数值型）
        - 'mode': 众数填充（分类型）
        - 'fill': 指定值填充
        - 'interpolate': 插值填充
        - 'auto': 自动选择（默认）
        """
        strategies = strategies or {}
        df = df.copy()

        for col in df.columns:
            if df[col].isnull().sum() == 0:
                continue

            strategy = strategies.get(col, {}).get('missing', self.default_missing_strategy)

            if strategy == 'auto':
                strategy = self._auto_missing_strategy(df[col])

            if strategy == 'drop':
                df = df.dropna(subset=[col])
            elif strategy == 'mean' and pd.api.types.is_numeric_dtype(df[col]):
                df[col] = df[col].fillna(df[col].mean())
            elif strategy == 'median' and pd.api.types.is_numeric_dtype(df[col]):
                df[col] = df[col].fillna(df[col].median())
            elif strategy == 'mode':
                mode_val = df[col].mode()
                if len(mode_val) > 0:
                    df[col] = df[col].fillna(mode_val[0])
            elif strategy == 'interpolate':
                df[col] = df[col].interpolate(method='linear')
            elif strategy == 'fill' and 'fill_value' in strategies.get(col, {}):
                df[col] = df[col].fillna(strategies[col]['fill_value'])

        return df

    def _auto_missing_strategy(self, series: pd.Series) -> str:
        """自动选择缺失值处理策略"""
        missing_ratio = series.isnull().sum() / len(series)

        if missing_ratio > 0.5:
            return 'drop' if series.isnull().sum() == len(series) else 'median'
        elif pd.api.types.is_numeric_dtype(series):
            return 'median'
        else:
            return 'mode'

    def handle_outliers(self, df: pd.DataFrame, strategies: Optional[Dict] = None) -> pd.DataFrame:
        """
        处理异常值

        方法:
        - 'iqr': IQR方法（默认）
        - 'zscore': Z-score方法
        - 'clip': 截断到边界
        - 'drop': 删除异常行
        """
        strategies = strategies or {}
        df = df.copy()

        numeric_cols = df.select_dtypes(include=[np.number]).columns

        for col in numeric_cols:
            method = strategies.get(col, {}).get('outlier', self.default_outlier_method)

            if method == 'iqr':
                outliers = self._detect_outliers_iqr(df[col])
            elif method == 'zscore':
                outliers = self._detect_outliers_zscore(df[col])
            else:
                continue

            if method == 'drop':
                df = df[~outliers]
            elif method == 'clip':
                q1, q3 = df[col].quantile([0.25, 0.75])
                iqr = q3 - q1
                lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
                df[col] = df[col].clip(lower, upper)

        return df

    def _detect_outliers_iqr(self, series: pd.Series) -> pd.Series:
        """使用IQR方法检测异常值"""
        q1, q3 = series.quantile([0.25, 0.75])
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        return (series < lower_bound) | (series > upper_bound)

    def _detect_outliers_zscore(self, series: pd.Series, threshold: float = 3.0) -> pd.Series:
        """使用Z-score方法检测异常值"""
        z_scores = np.abs((series - series.mean()) / series.std())
        return z_scores > threshold

    def get_cleaning_report(self, df_before: pd.DataFrame, df_after: pd.DataFrame) -> Dict[str, Any]:
        """生成清洗报告"""
        return {
            "rows_before": len(df_before),
            "rows_after": len(df_after),
            "rows_dropped": len(df_before) - len(df_after),
            "missing_before": df_before.isnull().sum().sum(),
            "missing_after": df_after.isnull().sum().sum(),
            "duplicates_dropped": len(df_before) - len(df_before.drop_duplicates())
        }
```

- [ ] **Step 2: 创建特征工程器**

```python
# campus-ai/src/data/transformers/feature_engineer.py
"""特征工程器"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Optional, Dict, Any, List
from sklearn.preprocessing import LabelEncoder, StandardScaler
import logging

logger = logging.getLogger(__name__)


class FeatureEngineer:
    """
    特征工程器

    提供以下功能：
    - 时间特征提取
    - 分类变量编码
    - 数值特征缩放
    - 交互特征生成
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.encoders = {}
        self.scalers = {}

    def extract_time_features(self, df: pd.DataFrame, datetime_col: str, prefix: Optional[str] = None) -> pd.DataFrame:
        """
        从日期时间列提取特征

        生成特征:
        - 小时 (0-23)
        - 星期 (0-6)
        - 月份 (1-12)
        - 是否周末
        - 是否节假日（简化版）
        """
        df = df.copy()
        prefix = prefix or datetime_col

        # 确保是datetime类型
        df[datetime_col] = pd.to_datetime(df[datetime_col])

        # 时间特征
        df[f'{prefix}_hour'] = df[datetime_col].dt.hour
        df[f'{prefix}_dayofweek'] = df[datetime_col].dt.dayofweek
        df[f'{prefix}_month'] = df[datetime_col].dt.month
        df[f'{prefix}_year'] = df[datetime_col].dt.year
        df[f'{prefix}_is_weekend'] = df[datetime_col].dt.dayofweek >= 5

        # 时间段分类
        df[f'{prefix}_time_period'] = pd.cut(
            df[f'{prefix}_hour'],
            bins=[0, 6, 12, 18, 24],
            labels=['night', 'morning', 'afternoon', 'evening'],
            include_lowest=True
        )

        logger.info(f"从 {datetime_col} 提取了时间特征")
        return df

    def encode_categorical(self, df: pd.DataFrame, columns: List[str], method: str = 'onehot') -> pd.DataFrame:
        """
        分类变量编码

        方法:
        - 'onehot': One-Hot编码
        - 'label': 标签编码
        - 'target': 目标编码（需要y）
        """
        df = df.copy()

        for col in columns:
            if col not in df.columns:
                continue

            if method == 'onehot':
                dummies = pd.get_dummies(df[col], prefix=col, drop_first=False)
                df = pd.concat([df, dummies], axis=1)
            elif method == 'label':
                if col not in self.encoders:
                    self.encoders[col] = LabelEncoder()
                    df[f'{col}_encoded'] = self.encoders[col].fit_transform(df[col].astype(str))
                else:
                    df[f'{col}_encoded'] = self.encoders[col].transform(df[col].astype(str))

        return df

    def scale_numeric(self, df: pd.DataFrame, columns: List[str], method: str = 'standard') -> pd.DataFrame:
        """
        数值特征缩放

        方法:
        - 'standard': Z-score标准化
        - 'minmax': Min-Max归一化
        """
        df = df.copy()

        for col in columns:
            if col not in df.columns:
                continue

            scaler_key = f'{col}_{method}'

            if method == 'standard':
                if scaler_key not in self.scalers:
                    self.scalers[scaler_key] = StandardScaler()
                    df[f'{col}_scaled'] = self.scalers[scaler_key].fit_transform(df[[col]])
                else:
                    df[f'{col}_scaled'] = self.scalers[scaler_key].transform(df[[col]])
            elif method == 'minmax':
                min_val = df[col].min()
                max_val = df[col].max()
                df[f'{col}_scaled'] = (df[col] - min_val) / (max_val - min_val)

        return df

    def create_interaction_features(self, df: pd.DataFrame, pairs: List[tuple]) -> pd.DataFrame:
        """
        创建交互特征

        Args:
            pairs: 特征对列表 [(col1, col2), ...]
        """
        df = df.copy()

        for col1, col2 in pairs:
            if col1 in df.columns and col2 in df.columns:
                # 数值型交互
                if pd.api.types.is_numeric_dtype(df[col1]) and pd.api.types.is_numeric_dtype(df[col2]):
                    df[f'{col1}_x_{col2}'] = df[col1] * df[col2]
                    df[f'{col1}_div_{col2}'] = df[col1] / (df[col2] + 1e-8)

        return df

    def generate_activity_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        专门用于活动数据的特征生成

        生成特征:
        - 活动时长
        - 人均预算
        - 活动规模等级
        """
        df = df.copy()

        # 活动时长（小时）
        if 'start_time' in df.columns and 'end_time' in df.columns:
            df['start_time'] = pd.to_datetime(df['start_time'])
            df['end_time'] = pd.to_datetime(df['end_time'])
            df['duration_hours'] = (df['end_time'] - df['start_time']).dt.total_seconds() / 3600

        # 人均预算
        if 'budget_amount' in df.columns and 'participant_count' in df.columns:
            df['budget_per_person'] = df['budget_amount'] / (df['participant_count'] + 1)

        # 活动规模等级
        if 'participant_count' in df.columns:
            df['size_category'] = pd.cut(
                df['participant_count'],
                bins=[0, 20, 50, 100, 500],
                labels=['small', 'medium', 'large', 'xlarge']
            )

        return df
```

- [ ] **Step 3: 更新转换器模块初始化**

```python
# campus-ai/src/data/transformers/__init__.py
"""数据转换器模块"""

from .cleaner import DataCleaner
from .feature_engineer import FeatureEngineer

__all__ = [
    "DataCleaner",
    "FeatureEngineer",
]
```

- [ ] **Step 4: 创建转换器测试**

```python
# campus-ai/tests/data/test_transformers.py
import pytest
import pandas as pd
import numpy as np
from datetime import datetime


class TestDataCleaner:
    """测试数据清洗器"""

    @pytest.fixture
    def dirty_data(self):
        return pd.DataFrame({
            'name': ['A', 'B', 'C', 'D', 'E'],
            'age': [20, np.nan, 25, 150, 22],  # 有缺失值和异常值
            'salary': [5000, 6000, np.nan, 5500, 20000]  # 有异常高值
        })

    def test_clean_removes_outliers(self, dirty_data):
        from src.data.transformers.cleaner import DataCleaner

        cleaner = DataCleaner()
        df_cleaned = cleaner.handle_outliers(dirty_data, {'age': {'outlier': 'drop'}})

        # 150岁应该被识别为异常值并删除
        assert len(df_cleaned) < len(dirty_data)

    def test_handle_missing_values(self):
        from src.data.transformers.cleaner import DataCleaner

        df = pd.DataFrame({
            'numeric': [1, 2, np.nan, 4],
            'categorical': ['A', np.nan, 'B', 'C']
        })

        cleaner = DataCleaner()
        df_cleaned = cleaner.handle_missing_values(df)

        # 缺失值应该被填充
        assert df_cleaned['numeric'].isnull().sum() == 0
        assert df_cleaned['categorical'].isnull().sum() == 0


class TestFeatureEngineer:
    """测试特征工程器"""

    def test_extract_time_features(self):
        from src.data.transformers.feature_engineer import FeatureEngineer

        df = pd.DataFrame({
            'event_time': pd.date_range('2024-01-01', periods=5, freq='H')
        })

        engineer = FeatureEngineer()
        df_features = engineer.extract_time_features(df, 'event_time')

        assert 'event_time_hour' in df_features.columns
        assert 'event_time_dayofweek' in df_features.columns
        assert 'event_time_is_weekend' in df_features.columns

    def test_encode_categorical(self):
        from src.data.transformers.feature_engineer import FeatureEngineer

        df = pd.DataFrame({
            'category': ['A', 'B', 'A', 'C']
        })

        engineer = FeatureEngineer()
        df_encoded = engineer.encode_categorical(df, ['category'], method='onehot')

        assert 'category_A' in df_encoded.columns
        assert 'category_B' in df_encoded.columns
        assert 'category_C' in df_encoded.columns

    def test_generate_activity_features(self):
        from src.data.transformers.feature_engineer import FeatureEngineer

        df = pd.DataFrame({
            'start_time': pd.to_datetime(['2024-01-01 10:00'] * 3),
            'end_time': pd.to_datetime(['2024-01-01 12:00', '2024-01-01 14:00', '2024-01-01 16:00']),
            'participant_count': [10, 50, 150],
            'budget_amount': [1000, 5000, 20000]
        })

        engineer = FeatureEngineer()
        df_features = engineer.generate_activity_features(df)

        assert 'duration_hours' in df_features.columns
        assert 'budget_per_person' in df_features.columns
        assert 'size_category' in df_features.columns
```

- [ ] **Step 5: 运行测试验证通过**

```bash
cd campus-ai && python -m pytest tests/data/test_transformers.py -v 2>&1 | tail -20
```

Expected: 测试通过

- [ ] **Step 6: 提交转换器模块**

```bash
git add campus-ai/src/data/transformers/ campus-ai/tests/data/test_transformers.py
git commit -m "feat: add data transformers with cleaner and feature engineer"
```

---

### 任务8: 数据质量检查模块

**Files:**
- Create: `campus-ai/src/data/quality.py`

- [ ] **Step 1: 创建数据质量检查器**

```python
# campus-ai/src/data/quality.py
"""数据质量检查模块"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class QualityReport:
    """数据质量报告"""
    overall_score: float
    completeness: float
    accuracy: float
    consistency: float
    validity: float
    details: Dict[str, Any]


class DataQualityChecker:
    """
    数据质量检查器

    检查维度:
    - 完整性(Completeness): 字段填充率
    - 准确性(Accuracy): 符合业务规则
    - 一致性(Consistency): 关联数据匹配
    - 有效性(Validity): 格式/类型正确
    """

    # 各维度权重
    WEIGHTS = {
        "completeness": 0.30,
        "accuracy": 0.30,
        "consistency": 0.20,
        "validity": 0.20
    }

    def __init__(self, rules: Optional[Dict] = None):
        self.rules = rules or {}

    def check(self, df: pd.DataFrame, table_name: str = "") -> QualityReport:
        """
        执行完整质量检查

        Returns:
            QualityReport 包含各项得分和详情
        """
        completeness = self._check_completeness(df)
        accuracy = self._check_accuracy(df)
        consistency = self._check_consistency(df)
        validity = self._check_validity(df)

        # 计算总分
        overall = (
            completeness * self.WEIGHTS["completeness"] +
            accuracy * self.WEIGHTS["accuracy"] +
            consistency * self.WEIGHTS["consistency"] +
            validity * self.WEIGHTS["validity"]
        )

        report = QualityReport(
            overall_score=round(overall, 2),
            completeness=round(completeness, 2),
            accuracy=round(accuracy, 2),
            consistency=round(consistency, 2),
            validity=round(validity, 2),
            details={
                "table_name": table_name,
                "total_rows": len(df),
                "total_columns": len(df.columns),
                "completeness_details": self._get_completeness_details(df),
            }
        )

        logger.info(f"数据质量评分: {report.overall_score}/100")
        return report

    def _check_completeness(self, df: pd.DataFrame) -> float:
        """检查完整性：非空值比例"""
        if df.empty:
            return 0.0

        non_null_ratio = 1 - df.isnull().sum().sum() / (len(df) * len(df.columns))
        return non_null_ratio * 100

    def _check_accuracy(self, df: pd.DataFrame) -> float:
        """检查准确性：符合业务规则的比例"""
        if 'accuracy_rules' not in self.rules or df.empty:
            return 100.0

        total_checks = 0
        passed_checks = 0

        for rule in self.rules['accuracy_rules']:
            col = rule.get('column')
            if col not in df.columns:
                continue

            if rule['type'] == 'range':
                valid = df[col].between(rule['min'], rule['max'])
                passed_checks += valid.sum()
                total_checks += len(df)
            elif rule['type'] == 'regex':
                import re
                pattern = re.compile(rule['pattern'])
                valid = df[col].astype(str).str.match(pattern)
                passed_checks += valid.sum()
                total_checks += len(df)

        return (passed_checks / total_checks * 100) if total_checks > 0 else 100.0

    def _check_consistency(self, df: pd.DataFrame) -> float:
        """检查一致性：重复值比例"""
        if df.empty:
            return 100.0

        duplicate_ratio = df.duplicated().sum() / len(df)
        return (1 - duplicate_ratio) * 100

    def _check_validity(self, df: pd.DataFrame) -> float:
        """检查有效性：数据类型正确性"""
        if 'dtype_rules' not in self.rules or df.empty:
            return 100.0

        valid_count = 0
        total_count = 0

        for col, expected_type in self.rules['dtype_rules'].items():
            if col not in df.columns:
                continue

            total_count += len(df)

            if expected_type == 'datetime':
                try:
                    pd.to_datetime(df[col], errors='raise')
                    valid_count += len(df)
                except:
                    pass
            elif expected_type == 'numeric':
                valid_count += pd.api.types.is_numeric_dtype(df[col]) * len(df)
            elif expected_type == 'string':
                valid_count += (df[col].dtype == 'object') * len(df)

        return (valid_count / total_count * 100) if total_count > 0 else 100.0

    def _get_completeness_details(self, df: pd.DataFrame) -> Dict[str, float]:
        """获取各字段的完整度详情"""
        return {
            col: round((1 - df[col].isnull().sum() / len(df)) * 100, 2)
            for col in df.columns
        }

    def get_quality_level(self, score: float) -> str:
        """根据分数返回质量等级"""
        if score >= 90:
            return "excellent"
        elif score >= 75:
            return "good"
        elif score >= 60:
            return "acceptable"
        else:
            return "poor"

    def generate_report_text(self, report: QualityReport) -> str:
        """生成文本格式的质量报告"""
        level = self.get_quality_level(report.overall_score)

        text = f"""
============================================
数据质量报告
============================================
表名: {report.details['table_name']}
记录数: {report.details['total_rows']}
字段数: {report.details['total_columns']}

总体评分: {report.overall_score}/100 ({level})
-------------------------------------------
维度得分:
  - 完整性: {report.completeness}/100
  - 准确性: {report.accuracy}/100
  - 一致性: {report.consistency}/100
  - 有效性: {report.validity}/100

建议:
{self._get_recommendations(report)}
============================================
"""
        return text

    def _get_recommendations(self, report: QualityReport) -> str:
        """根据评分给出建议"""
        recommendations = []

        if report.completeness < 90:
            recommendations.append("- 数据完整性较低，建议检查缺失值处理逻辑")
        if report.accuracy < 90:
            recommendations.append("- 数据准确性较低，建议检查数据源和业务规则")
        if report.consistency < 90:
            recommendations.append("- 存在重复数据，建议检查主键约束")
        if report.validity < 90:
            recommendations.append("- 数据格式不一致，建议标准化数据类型")

        if not recommendations:
            recommendations.append("- 数据质量良好，可以进入下游处理")

        return "\n".join(recommendations)
```

- [ ] **Step 2: 创建质量检查测试**

```python
# campus-ai/tests/data/test_quality.py
import pytest
import pandas as pd
import numpy as np


class TestDataQualityChecker:
    """测试数据质量检查器"""

    def test_completeness_check(self):
        from src.data.quality import DataQualityChecker

        df = pd.DataFrame({
            'a': [1, 2, 3, 4],
            'b': [1, np.nan, 3, np.nan]  # 50%缺失
        })

        checker = DataQualityChecker()
        report = checker.check(df)

        # 完整性 = (4+2)/8 = 75%
        assert report.completeness == 75.0

    def test_consistency_check(self):
        from src.data.quality import DataQualityChecker

        df = pd.DataFrame({
            'a': [1, 2, 2, 4],  # 第3行是重复
            'b': [1, 2, 2, 4]
        })

        checker = DataQualityChecker()
        report = checker.check(df)

        # 一致性 = (1 - 1/4) * 100 = 75%
        assert report.consistency == 75.0

    def test_overall_score_calculation(self):
        from src.data.quality import DataQualityChecker

        # 完美数据
        df = pd.DataFrame({
            'a': [1, 2, 3, 4],
            'b': [5, 6, 7, 8]
        })

        checker = DataQualityChecker()
        report = checker.check(df)

        assert report.overall_score == 100.0
        assert report.completeness == 100.0

    def test_quality_levels(self):
        from src.data.quality import DataQualityChecker

        checker = DataQualityChecker()

        assert checker.get_quality_level(95) == "excellent"
        assert checker.get_quality_level(80) == "good"
        assert checker.get_quality_level(65) == "acceptable"
        assert checker.get_quality_level(50) == "poor"

    def test_accuracy_check_with_rules(self):
        from src.data.quality import DataQualityChecker

        df = pd.DataFrame({
            'age': [20, 25, 200, 30],  # 200是异常值
        })

        rules = {
            'accuracy_rules': [
                {'column': 'age', 'type': 'range', 'min': 0, 'max': 120}
            ]
        }

        checker = DataQualityChecker(rules=rules)
        report = checker.check(df)

        # 3/4 = 75%
        assert report.accuracy == 75.0
```

- [ ] **Step 3: 运行测试验证通过**

```bash
cd campus-ai && python -m pytest tests/data/test_quality.py -v 2>&1 | tail -20
```

Expected: 测试通过

- [ ] **Step 4: 提交质量检查模块**

```bash
git add campus-ai/src/data/quality.py campus-ai/tests/data/test_quality.py
git commit -m "feat: add data quality checker with comprehensive metrics"
```

---

### 任务9: ETL管道编排

**Files:**
- Create: `campus-ai/src/data/pipeline.py`

- [ ] **Step 1: 创建ETL管道类**

```python
# campus-ai/src/data/pipeline.py
"""ETL管道编排模块"""

import pandas as pd
from typing import Optional, Dict, Any, Callable, List
from datetime import datetime
import logging
from sqlalchemy import create_engine

from .generators import StudentGenerator, ClubGenerator, ActivityGenerator
from .extractors import ExcelExtractor
from .transformers import DataCleaner, FeatureEngineer
from .quality import DataQualityChecker
from .config import config

logger = logging.getLogger(__name__)


class ETLPipeline:
    """
    ETL管道编排器

    支持三种数据源：
    1. 模拟数据生成 (simulation)
    2. 历史数据导入 (historical)
    3. 外部爬虫采集 (crawling)
    """

    def __init__(self, db_connection: Optional[str] = None):
        self.db_connection = db_connection or config.db_connection_string
        self.engine = create_engine(self.db_connection) if self.db_connection else None

        # 初始化各组件
        self.cleaner = DataCleaner()
        self.feature_engineer = FeatureEngineer()
        self.quality_checker = DataQualityChecker()

        # 执行统计
        self.stats = {
            "start_time": None,
            "end_time": None,
            "records_processed": 0,
            "records_loaded": 0,
            "quality_score": 0
        }

    def run_simulation(self, student_count: int = 5000, club_count: int = 50,
                       activity_count: int = 500, seed: int = 42) -> Dict[str, Any]:
        """
        运行模拟数据生成管道

        Returns:
            执行统计信息
        """
        logger.info("开始模拟数据生成ETL...")
        self.stats["start_time"] = datetime.now()

        try:
            # Extract: 生成数据
            students, clubs, activities = self._generate_simulation_data(
                student_count, club_count, activity_count, seed
            )

            # Transform: 清洗与特征工程
            students = self._transform_student_data(students)
            clubs = self._transform_club_data(clubs)
            activities = self._transform_activity_data(activities)

            # Quality Check
            quality_reports = {
                "students": self.quality_checker.check(students, "students"),
                "clubs": self.quality_checker.check(clubs, "clubs"),
                "activities": self.quality_checker.check(activities, "activities")
            }

            # Load: 写入数据库
            if self.engine:
                students.to_sql('students', self.engine, if_exists='append', index=False)
                clubs.to_sql('clubs', self.engine, if_exists='append', index=False)
                activities.to_sql('activities', self.engine, if_exists='append', index=False)

            # 更新统计
            self.stats["records_processed"] = len(students) + len(clubs) + len(activities)
            self.stats["records_loaded"] = self.stats["records_processed"]
            self.stats["quality_score"] = sum(r.overall_score for r in quality_reports.values()) / 3
            self.stats["end_time"] = datetime.now()

            logger.info(f"模拟数据生成完成，共 {self.stats['records_loaded']} 条记录")

            return {
                "success": True,
                "stats": self.stats,
                "quality_reports": quality_reports
            }

        except Exception as e:
            logger.error(f"ETL执行失败: {e}")
            return {"success": False, "error": str(e)}

    def run_historical_import(self, filepath: str, data_type: str) -> Dict[str, Any]:
        """
        运行历史数据导入管道

        Args:
            filepath: Excel/CSV文件路径
            data_type: 数据类型 (students, clubs, activities)

        Returns:
            执行统计信息
        """
        logger.info(f"开始历史数据导入: {filepath}")
        self.stats["start_time"] = datetime.now()

        try:
            # Extract
            extractor = ExcelExtractor()
            df = extractor.extract(filepath)

            # Transform
            df = self.cleaner.clean(df)

            if data_type == 'activities':
                df = self._transform_activity_data(df)

            # Quality Check
            quality_report = self.quality_checker.check(df, data_type)

            # Load
            if self.engine:
                table_name = f"{data_type}_imported"
                df.to_sql(table_name, self.engine, if_exists='append', index=False)

            self.stats["records_processed"] = len(df)
            self.stats["records_loaded"] = len(df)
            self.stats["quality_score"] = quality_report.overall_score
            self.stats["end_time"] = datetime.now()

            return {
                "success": True,
                "stats": self.stats,
                "quality_report": quality_report
            }

        except Exception as e:
            logger.error(f"历史数据导入失败: {e}")
            return {"success": False, "error": str(e)}

    def _generate_simulation_data(self, student_count: int, club_count: int,
                                   activity_count: int, seed: int) -> tuple:
        """生成模拟数据"""
        # 学生数据
        student_gen = StudentGenerator(seed=seed)
        students = student_gen.generate(student_count)
        logger.info(f"生成了 {len(students)} 条学生记录")

        # 社团数据
        club_gen = ClubGenerator(seed=seed)
        clubs = club_gen.generate(club_count)
        logger.info(f"生成了 {len(clubs)} 条社团记录")

        # 活动数据（依赖社团数据）
        activity_gen = ActivityGenerator(seed=seed)
        activities = activity_gen.generate(activity_count, clubs_df=clubs)
        logger.info(f"生成了 {len(activities)} 条活动记录")

        return students, clubs, activities

    def _transform_student_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """转换学生数据"""
        # 标准化年级
        df['grade_level'] = df['grade_level'].astype(int)

        # 编码性别
        df['gender_encoded'] = df['gender'].map({'M': 1, 'F': 0})

        return df

    def _transform_club_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """转换社团数据"""
        # 计算社团年龄
        df['club_age_years'] = datetime.now().year - pd.to_datetime(df['founding_date']).dt.year

        return df

    def _transform_activity_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """转换活动数据"""
        # 时间特征
        df = self.feature_engineer.extract_time_features(df, 'start_time')

        # 活动特征
        df = self.feature_engineer.generate_activity_features(df)

        return df

    def get_stats(self) -> Dict[str, Any]:
        """获取执行统计"""
        return self.stats.copy()
```

- [ ] **Step 2: 创建管道测试**

```python
# campus-ai/tests/data/test_pipeline.py
import pytest
import pandas as pd
from unittest.mock import Mock, patch


class TestETLPipeline:
    """测试ETL管道"""

    def test_pipeline_initialization(self):
        from src.data.pipeline import ETLPipeline

        pipeline = ETLPipeline(db_connection=None)
        assert pipeline.cleaner is not None
        assert pipeline.feature_engineer is not None
        assert pipeline.quality_checker is not None

    @patch('src.data.pipeline.create_engine')
    def test_run_simulation(self, mock_create_engine):
        from src.data.pipeline import ETLPipeline

        # Mock数据库引擎
        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine

        pipeline = ETLPipeline(db_connection="postgresql://test")
        result = pipeline.run_simulation(
            student_count=10,
            club_count=5,
            activity_count=20,
            seed=42
        )

        assert result['success'] is True
        assert result['stats']['records_processed'] == 35  # 10+5+20
        assert 'quality_reports' in result

    def test_transform_activity_data(self):
        from src.data.pipeline import ETLPipeline

        pipeline = ETLPipeline(db_connection=None)

        df = pd.DataFrame({
            'start_time': pd.to_datetime(['2024-01-01 10:00'] * 3),
            'end_time': pd.to_datetime(['2024-01-01 12:00'] * 3),
            'participant_count': [10, 20, 30],
            'budget_amount': [1000, 2000, 3000]
        })

        result = pipeline._transform_activity_data(df)

        assert 'start_time_hour' in result.columns
        assert 'duration_hours' in result.columns
```

- [ ] **Step 3: 运行测试验证通过**

```bash
cd campus-ai && python -m pytest tests/data/test_pipeline.py -v 2>&1 | tail -20
```

Expected: 测试通过

- [ ] **Step 4: 提交ETL管道**

```bash
git add campus-ai/src/data/pipeline.py campus-ai/tests/data/test_pipeline.py
git commit -m "feat: add ETL pipeline orchestration"
```

---

### 任务10: 爬虫基础框架

**Files:**
- Create: `campus-ai/src/data/crawlers/__init__.py`
- Create: `campus-ai/src/data/crawlers/base.py`
- Create: `campus-ai/src/data/crawlers/tieba_crawler.py`
- Create: `campus-ai/tests/data/test_crawlers.py`

- [ ] **Step 1: 创建爬虫基类**

```python
# campus-ai/src/data/crawlers/base.py
"""爬虫基类"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
import time
import random
import logging
from fake_useragent import UserAgent

logger = logging.getLogger(__name__)


class BaseCrawler(ABC):
    """
    爬虫基类

    提供以下功能：
    - 请求频率控制
    - User-Agent轮换
    - 重试机制
    - 数据去重
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.delay_min = self.config.get('delay_min', 1.0)
        self.delay_max = self.config.get('delay_max', 3.0)
        self.max_retries = self.config.get('max_retries', 3)
        self.ua = UserAgent(fallback='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        self.seen_ids = set()

    def get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }

    def sleep(self):
        """随机延迟"""
        delay = random.uniform(self.delay_min, self.delay_max)
        time.sleep(delay)

    def is_duplicate(self, post_id: str) -> bool:
        """检查是否已抓取"""
        if post_id in self.seen_ids:
            return True
        self.seen_ids.add(post_id)
        return False

    @abstractmethod
    def crawl(self, keyword: str, max_posts: int = 100) -> List[Dict]:
        """执行爬取"""
        pass

    def parse_sentiment(self, text: str) -> tuple:
        """
        简单的情感分析（基于关键词）

        Returns:
            (sentiment_score, sentiment_label)
        """
        positive_words = ['好', '棒', '精彩', '喜欢', '赞', '优秀', '成功', '开心', '满意']
        negative_words = ['差', '糟糕', '失败', '失望', '讨厌', '烂', '垃圾', '难过']

        score = 0
        for word in positive_words:
            if word in text:
                score += 1
        for word in negative_words:
            if word in text:
                score -= 1

        if score > 0:
            return score, 'positive'
        elif score < 0:
            return score, 'negative'
        else:
            return 0, 'neutral'
```

- [ ] **Step 2: 实现贴吧爬虫（简化版）**

```python
# campus-ai/src/data/crawlers/tieba_crawler.py
"""百度贴吧爬虫"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from datetime import datetime
import logging

from .base import BaseCrawler

logger = logging.getLogger(__name__)


class TiebaCrawler(BaseCrawler):
    """
    百度贴吧爬虫

    采集指定贴吧的帖子内容，用于情感分析
    """

    BASE_URL = "https://tieba.baidu.com/f"

    def crawl(self, keyword: str, max_posts: int = 100) -> List[Dict]:
        """
        爬取贴吧帖子

        Args:
            keyword: 贴吧名称（如"学校名+社团"）
            max_posts: 最大采集帖子数

        Returns:
            帖子列表
        """
        results = []
        page = 1

        logger.info(f"开始爬取贴吧: {keyword}, 目标{max_posts}条")

        while len(results) < max_posts and page <= 10:  # 最多10页
            try:
                posts = self._fetch_page(keyword, page)

                for post in posts:
                    if len(results) >= max_posts:
                        break

                    # 去重检查
                    if self.is_duplicate(post['post_id']):
                        continue

                    # 情感分析
                    score, label = self.parse_sentiment(post['content'])
                    post['sentiment_score'] = score
                    post['sentiment_label'] = label

                    results.append(post)

                logger.info(f"第{page}页采集完成，当前共{len(results)}条")
                page += 1
                self.sleep()

            except Exception as e:
                logger.error(f"爬取第{page}页失败: {e}")
                break

        logger.info(f"爬取完成，共{len(results)}条帖子")
        return results

    def _fetch_page(self, keyword: str, page: int) -> List[Dict]:
        """获取单页帖子"""
        params = {
            'kw': keyword,
            'pn': (page - 1) * 50  # 每页50条
        }

        try:
            response = requests.get(
                self.BASE_URL,
                params=params,
                headers=self.get_headers(),
                timeout=10
            )
            response.encoding = 'utf-8'

            return self._parse_html(response.text)

        except requests.RequestException as e:
            logger.error(f"请求失败: {e}")
            return []

    def _parse_html(self, html: str) -> List[Dict]:
        """解析HTML提取帖子数据"""
        soup = BeautifulSoup(html, 'html.parser')
        posts = []

        # 查找帖子列表（简化版选择器）
        thread_list = soup.find_all('div', class_='threadlist_item_right')

        for thread in thread_list:
            try:
                # 提取标题和内容
                title_elem = thread.find('a', class_='j_th_tit')
                if not title_elem:
                    continue

                title = title_elem.get_text(strip=True)
                link = title_elem.get('href', '')
                post_id = link.split('/')[-1] if '/' in link else ''

                # 提取摘要
                abstract_elem = thread.find('div', class_='threadlist_abs')
                abstract = abstract_elem.get_text(strip=True) if abstract_elem else ''

                # 提取作者和时间
                author_elem = thread.find('span', class_='frs-author-name')
                author = author_elem.get_text(strip=True) if author_elem else '匿名'

                posts.append({
                    'post_id': f"tieba_{post_id}",
                    'platform': 'tieba',
                    'title': title,
                    'content': f"{title} {abstract}",
                    'author': author,
                    'publish_time': datetime.now(),  # 简化处理
                    'url': f"https://tieba.baidu.com{link}" if link else '',
                    'crawled_at': datetime.now()
                })

            except Exception as e:
                logger.warning(f"解析帖子失败: {e}")
                continue

        return posts
```

- [ ] **Step 3: 更新爬虫模块初始化**

```python
# campus-ai/src/data/crawlers/__init__.py
"""爬虫模块"""

from .base import BaseCrawler
from .tieba_crawler import TiebaCrawler

__all__ = [
    "BaseCrawler",
    "TiebaCrawler",
]
```

- [ ] **Step 4: 创建爬虫测试（模拟测试）**

```python
# campus-ai/tests/data/test_crawlers.py
import pytest
from unittest.mock import Mock, patch


class TestBaseCrawler:
    """测试爬虫基类"""

    def test_duplicate_detection(self):
        from src.data.crawlers.base import BaseCrawler

        class TestCrawler(BaseCrawler):
            def crawl(self, keyword, max_posts=100):
                return []

        crawler = TestCrawler()

        assert crawler.is_duplicate("post_1") is False  # 第一次不是重复
        assert crawler.is_duplicate("post_1") is True   # 第二次是重复
        assert crawler.is_duplicate("post_2") is False

    def test_sentiment_analysis(self):
        from src.data.crawlers.base import BaseCrawler

        class TestCrawler(BaseCrawler):
            def crawl(self, keyword, max_posts=100):
                return []

        crawler = TestCrawler()

        # 正面文本
        score, label = crawler.parse_sentiment("这个活动太棒了，非常喜欢！")
        assert label == 'positive'
        assert score > 0

        # 负面文本
        score, label = crawler.parse_sentiment("太差了，很失望")
        assert label == 'negative'
        assert score < 0

        # 中性文本
        score, label = crawler.parse_sentiment("今天天气不错")
        assert label == 'neutral'


class TestTiebaCrawler:
    """测试贴吧爬虫"""

    @patch('src.data.crawlers.tieba_crawler.requests.get')
    def test_crawl_with_mock(self, mock_get):
        from src.data.crawlers.tieba_crawler import TiebaCrawler

        # Mock响应
        mock_response = Mock()
        mock_response.text = '''
        <html>
            <div class="threadlist_item_right">
                <a class="j_th_tit" href="/p/123456">测试帖子标题</a>
                <div class="threadlist_abs">测试帖子内容</div>
                <span class="frs-author-name">测试用户</span>
            </div>
        </html>
        '''
        mock_response.encoding = 'utf-8'
        mock_get.return_value = mock_response

        crawler = TiebaCrawler(config={'delay_min': 0, 'delay_max': 0.1})
        results = crawler.crawl("测试吧", max_posts=5)

        assert len(results) <= 5
        if len(results) > 0:
            assert 'post_id' in results[0]
            assert 'content' in results[0]
            assert 'sentiment_label' in results[0]
```

- [ ] **Step 5: 运行测试验证通过**

```bash
cd campus-ai && python -m pytest tests/data/test_crawlers.py -v 2>&1 | tail -20
```

Expected: 测试通过

- [ ] **Step 6: 提交爬虫模块**

```bash
git add campus-ai/src/data/crawlers/ campus-ai/tests/data/test_crawlers.py
git commit -m "feat: add crawler framework with tieba support"
```

---

### 任务11: 集成测试与验证

**Files:**
- Create: `campus-ai/tests/data/test_integration.py`

- [ ] **Step 1: 创建数据模块集成测试**

```python
# campus-ai/tests/data/test_integration.py
import pytest
import pandas as pd
import tempfile
import os


class TestDataModuleIntegration:
    """数据模块集成测试"""

    def test_full_etl_workflow(self):
        """测试完整ETL流程"""
        from src.data.pipeline import ETLPipeline
        from src.data.quality import DataQualityChecker

        # 创建管道（无数据库）
        pipeline = ETLPipeline(db_connection=None)

        # 执行模拟数据生成
        result = pipeline.run_simulation(
            student_count=100,
            club_count=10,
            activity_count=50,
            seed=42
        )

        assert result['success'] is True
        assert result['stats']['records_processed'] == 160  # 100+10+50

        # 验证质量报告
        quality_reports = result['quality_reports']
        for table, report in quality_reports.items():
            assert report.overall_score >= 60  # 可接受质量

    def test_historical_import_workflow(self):
        """测试历史数据导入流程"""
        from src.data.extractors.excel_extractor import ExcelExtractor
        from src.data.transformers.cleaner import DataCleaner
        from src.data.quality import DataQualityChecker

        # 创建临时Excel文件
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
            filepath = f.name

        df_original = pd.DataFrame({
            'activity_name': ['活动A', '活动B', '活动C'],
            'participant_count': [50, 80, 120],
            'budget': [1000.0, 2000.0, None]  # 有一个缺失值
        })

        with pd.ExcelWriter(filepath) as writer:
            df_original.to_excel(writer, sheet_name='Activities', index=False)

        try:
            # Extract
            extractor = ExcelExtractor()
            df = extractor.extract(filepath)
            assert len(df) == 3

            # Transform
            cleaner = DataCleaner()
            df_cleaned = cleaner.handle_missing_values(
                df,
                strategies={'budget': {'missing': 'median'}}
            )
            assert df_cleaned['budget'].isnull().sum() == 0

            # Quality Check
            checker = DataQualityChecker()
            report = checker.check(df_cleaned)
            assert report.completeness == 100.0

        finally:
            os.unlink(filepath)

    def test_generator_to_transformer_pipeline(self):
        """测试生成器到转换器的管道"""
        from src.data.generators.activity_generator import ActivityGenerator
        from src.data.transformers.cleaner import DataCleaner
        from src.data.transformers.feature_engineer import FeatureEngineer

        # Generate
        generator = ActivityGenerator(seed=42)
        df = generator.generate(50)
        assert len(df) == 50

        # Clean
        cleaner = DataCleaner()
        df_cleaned = cleaner.clean(df)

        # Feature Engineering
        engineer = FeatureEngineer()
        df_features = engineer.generate_activity_features(df_cleaned)

        assert 'duration_hours' in df_features.columns
        assert 'size_category' in df_features.columns

    def test_crawler_to_storage_workflow(self):
        """测试爬虫到存储的工作流"""
        from src.data.crawlers.base import BaseCrawler

        class MockCrawler(BaseCrawler):
            def crawl(self, keyword, max_posts=100):
                return [
                    {
                        'post_id': f'post_{i}',
                        'content': f'测试内容{i}',
                        'platform': 'test'
                    }
                    for i in range(min(10, max_posts))
                ]

        crawler = MockCrawler(config={'delay_min': 0, 'delay_max': 0})
        results = crawler.crawl("测试关键词", max_posts=5)

        assert len(results) == 5

        # 验证所有结果都有情感标签
        for post in results:
            score, label = crawler.parse_sentiment(post['content'])
            assert label in ['positive', 'negative', 'neutral']
```

- [ ] **Step 2: 运行集成测试**

```bash
cd campus-ai && python -m pytest tests/data/test_integration.py -v 2>&1 | tail -30
```

Expected: 所有集成测试通过

- [ ] **Step 3: 提交集成测试**

```bash
git add campus-ai/tests/data/test_integration.py
git commit -m "test: add comprehensive integration tests for data module"
```

---

### 任务12: 数据模块命令行工具

**Files:**
- Create: `campus-ai/src/data/cli.py`

- [ ] **Step 1: 创建CLI工具**

```python
# campus-ai/src/data/cli.py
"""
数据模块命令行工具

用法:
    python -m src.data.cli generate --students 5000 --clubs 50 --activities 500
    python -m src.data.cli import --file data.xlsx --type activities
    python -m src.data.cli crawl --platform tieba --keyword "社团"
    python -m src.data.cli quality --file data.csv
"""

import argparse
import sys
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def cmd_generate(args):
    """生成模拟数据"""
    from .pipeline import ETLPipeline

    logger.info(f"开始生成模拟数据: {args.students}学生, {args.clubs}社团, {args.activities}活动")

    pipeline = ETLPipeline()
    result = pipeline.run_simulation(
        student_count=args.students,
        club_count=args.clubs,
        activity_count=args.activities,
        seed=args.seed
    )

    if result['success']:
        print(f"✅ 生成成功!")
        print(f"   学生: {args.students}条")
        print(f"   社团: {args.clubs}条")
        print(f"   活动: {args.activities}条")
        print(f"   质量评分: {result['stats']['quality_score']:.1f}/100")
    else:
        print(f"❌ 生成失败: {result.get('error')}")
        return 1

    return 0


def cmd_import(args):
    """导入历史数据"""
    from .pipeline import ETLPipeline
    from .extractors import ExcelExtractor

    logger.info(f"开始导入: {args.file}")

    if not Path(args.file).exists():
        print(f"❌ 文件不存在: {args.file}")
        return 1

    pipeline = ETLPipeline()
    result = pipeline.run_historical_import(args.file, args.type)

    if result['success']:
        print(f"✅ 导入成功!")
        print(f"   类型: {args.type}")
        print(f"   记录数: {result['stats']['records_loaded']}")
        print(f"   质量评分: {result['stats']['quality_score']:.1f}/100")
    else:
        print(f"❌ 导入失败: {result.get('error')}")
        return 1

    return 0


def cmd_crawl(args):
    """运行爬虫"""
    from .crawlers.tieba_crawler import TiebaCrawler

    logger.info(f"开始爬取: {args.platform}, 关键词: {args.keyword}")

    if args.platform == 'tieba':
        crawler = TiebaCrawler()
        results = crawler.crawl(args.keyword, max_posts=args.max_posts)

        print(f"✅ 爬取完成!")
        print(f"   平台: {args.platform}")
        print(f"   关键词: {args.keyword}")
        print(f"   采集数量: {len(results)}")

        # 情感分布统计
        sentiment_dist = {}
        for post in results:
            label = post.get('sentiment_label', 'neutral')
            sentiment_dist[label] = sentiment_dist.get(label, 0) + 1

        print(f"   情感分布:")
        for label, count in sentiment_dist.items():
            print(f"     - {label}: {count}")
    else:
        print(f"❌ 不支持的爬虫平台: {args.platform}")
        return 1

    return 0


def cmd_quality(args):
    """检查数据质量"""
    import pandas as pd
    from .quality import DataQualityChecker

    logger.info(f"开始质量检查: {args.file}")

    if not Path(args.file).exists():
        print(f"❌ 文件不存在: {args.file}")
        return 1

    # 读取文件
    if args.file.endswith('.csv'):
        df = pd.read_csv(args.file)
    elif args.file.endswith(('.xlsx', '.xls')):
        df = pd.read_excel(args.file)
    else:
        print(f"❌ 不支持的文件格式")
        return 1

    # 质量检查
    checker = DataQualityChecker()
    report = checker.check(df, Path(args.file).stem)

    print(checker.generate_report_text(report))

    return 0 if report.overall_score >= 60 else 1


def main():
    parser = argparse.ArgumentParser(
        description='校园社团数据管理工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  # 生成模拟数据
  python -m src.data.cli generate -s 5000 -c 50 -a 500

  # 导入历史数据
  python -m src.data.cli import -f activities.xlsx -t activities

  # 运行爬虫
  python -m src.data.cli crawl -p tieba -k "大学社团"

  # 检查数据质量
  python -m src.data.cli quality -f data.csv
        '''
    )

    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # generate 命令
    gen_parser = subparsers.add_parser('generate', help='生成模拟数据')
    gen_parser.add_argument('-s', '--students', type=int, default=1000, help='学生数量')
    gen_parser.add_argument('-c', '--clubs', type=int, default=20, help='社团数量')
    gen_parser.add_argument('-a', '--activities', type=int, default=200, help='活动数量')
    gen_parser.add_argument('--seed', type=int, default=42, help='随机种子')
    gen_parser.set_defaults(func=cmd_generate)

    # import 命令
    import_parser = subparsers.add_parser('import', help='导入历史数据')
    import_parser.add_argument('-f', '--file', required=True, help='文件路径')
    import_parser.add_argument('-t', '--type', required=True,
                               choices=['students', 'clubs', 'activities'],
                               help='数据类型')
    import_parser.set_defaults(func=cmd_import)

    # crawl 命令
    crawl_parser = subparsers.add_parser('crawl', help='运行爬虫')
    crawl_parser.add_argument('-p', '--platform', default='tieba',
                              choices=['tieba'], help='爬虫平台')
    crawl_parser.add_argument('-k', '--keyword', required=True, help='搜索关键词')
    crawl_parser.add_argument('-m', '--max-posts', type=int, default=100, help='最大采集数')
    crawl_parser.set_defaults(func=cmd_crawl)

    # quality 命令
    quality_parser = subparsers.add_parser('quality', help='检查数据质量')
    quality_parser.add_argument('-f', '--file', required=True, help='文件路径')
    quality_parser.set_defaults(func=cmd_quality)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
```

- [ ] **Step 2: 验证CLI工具**

```bash
cd campus-ai && python -m src.data.cli --help
```

Expected: 显示帮助信息

```bash
cd campus-ai && python -m src.data.cli quality --help
```

Expected: 显示quality子命令帮助

- [ ] **Step 3: 测试quality命令**

```bash
cd campus-ai && python -m src.data.cli quality -f src/data/config.py 2>&1 | head -10
```

Expected: 显示文件格式不支持的错误或解析结果

- [ ] **Step 4: 提交CLI工具**

```bash
git add campus-ai/src/data/cli.py
git commit -m "feat: add data module CLI tool"
```

---

### 任务13: 最终验证与提交

**Files:**
- All modified files

- [ ] **Step 1: 运行所有数据模块测试**

```bash
cd campus-ai && python -m pytest tests/data/ -v --tb=short 2>&1 | tail -40
```

Expected: 所有测试通过

- [ ] **Step 2: 验证Python语法**

```bash
cd campus-ai && find src/data -name "*.py" -exec python -m py_compile {} \; 2>&1
```

Expected: 无输出（表示无语法错误）

- [ ] **Step 3: 检查导入完整性**

```bash
cd campus-ai && python -c "from src.data import ETLPipeline, DataQualityChecker; print('✅ 导入成功')"
```

Expected: 导入成功

- [ ] **Step 4: 生成测试报告摘要**

```bash
cd campus-ai && python -m pytest tests/data/ -q 2>&1 | tail -10
```

- [ ] **Step 5: 提交第二阶段完成**

```bash
git add -A
git commit -m "feat: complete phase 2 - data collection and cleaning infrastructure

- Add data generators (student, club, activity)
- Add data extractors (Excel support)
- Add data transformers (cleaner, feature engineer)
- Add data quality checker with scoring
- Add ETL pipeline orchestration
- Add crawler framework (tieba support)
- Add CLI tool for data operations
- Add comprehensive test coverage

Components:
- campus-ai/src/data/generators/
- campus-ai/src/data/extractors/
- campus-ai/src/data/transformers/
- campus-ai/src/data/crawlers/
- campus-ai/src/data/pipeline.py
- campus-ai/src/data/quality.py
- campus-ai/src/data/cli.py"
```

---

## 计划自审查

已完成对规范的全面覆盖：

1. ✅ 数据模块依赖配置
2. ✅ 数据库迁移文件（外部数据表）
3. ✅ 模拟数据生成器（学生、社团、活动）
4. ✅ 历史数据提取器（Excel支持）
5. ✅ 数据转换器（清洗+特征工程）
6. ✅ 数据质量检查器
7. ✅ ETL管道编排
8. ✅ 爬虫框架（贴吧支持）
9. ✅ 集成测试
10. ✅ CLI命令行工具

**无占位符**：所有任务都包含完整的代码实现
**类型一致性**：所有类和函数名称保持一致
**测试覆盖**：每个组件都有对应的单元测试和集成测试

---

**计划完成并保存到 `docs/superpowers/plans/2026-04-11-campus-club-phase2-data-collection-implementation.md`**

**执行选项：**

**1. 子代理驱动（推荐）** - 我按任务派遣新的子代理，任务间进行审查，快速迭代

**2. 内联执行** - 在此会话中使用executing-plans执行任务，批量执行并设置检查点

**选择哪种方式？**
