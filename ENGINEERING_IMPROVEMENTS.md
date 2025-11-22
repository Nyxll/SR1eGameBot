# SR1eGameBot - Software Engineering Improvements

## Document Information
- **Perspective**: Senior Software Engineer
- **Date**: November 2025
- **Focus**: Architecture, code quality, scalability, and maintainability

---

## Executive Summary

While SR1eGameBot functions correctly, there are significant opportunities to improve the codebase's architecture, maintainability, scalability, and developer experience. These recommendations focus on modern software engineering practices, performance optimization, and future-proofing the application.

---

## 1. Architecture & Design Patterns

### Current Issues
- **Monolithic command handling**: All commands in single on_message handler
- **Global state**: Heavy reliance on global cache object
- **Tight coupling**: Database, encryption, and business logic intertwined
- **No dependency injection**: Hard to test and swap implementations
- **Missing abstractions**: Direct MongoDB calls throughout

### Recommended Improvements

#### 1.1 Adopt Clean Architecture
**Priority: HIGH**

Separate concerns into distinct layers:

```
sr1egamebot/
├── domain/           # Business logic (game rules, dice mechanics)
│   ├── entities/     # Domain models
│   ├── services/     # Business logic
│   └── interfaces/   # Abstract interfaces
├── application/      # Use cases (commands, workflows)
│   ├── commands/     # Command handlers
│   ├── queries/      # Query handlers
│   └── dto/          # Data transfer objects
├── infrastructure/   # External concerns
│   ├── database/     # Database implementations
│   ├── discord/      # Discord API wrapper
│   └── cache/        # Caching implementations
└── presentation/     # User interface layer
    └── discord_bot/  # Discord bot presentation
```

**Benefits:**
- Independent testability of each layer
- Easy to swap implementations (MongoDB → PostgreSQL)
- Clear separation of concerns
- Better code organization

#### 1.2 Implement Repository Pattern
**Priority: HIGH**

Abstract data access behind repositories:

```python
from abc import ABC, abstractmethod
from typing import Optional, List

class UserDataRepository(ABC):
    @abstractmethod
    async def get_user_data(
        self, 
        server_id: str, 
        channel_id: str, 
        user_id: str
    ) -> Optional[UserData]:
        pass
    
    @abstractmethod
    async def save_user_data(self, data: UserData) -> None:
        pass

class MongoUserDataRepository(UserDataRepository):
    def __init__(self, db: Database, encryptor: Encryptor, cache: Cache):
        self.db = db
        self.encryptor = encryptor
        self.cache = cache
    
    async def get_user_data(
        self, 
        server_id: str, 
        channel_id: str, 
        user_id: str
    ) -> Optional[UserData]:
        # Implementation with caching
        cache_key = f"{server_id}:{channel_id}:{user_id}"
        if cached := self.cache.get(cache_key):
            return cached
        
        # Fetch from database
        data = await self._fetch_from_db(server_id, channel_id, user_id)
        self.cache.set(cache_key, data)
        return data
```

**Benefits:**
- Easy to test with mock repositories
- Can swap database implementations
- Centralized caching logic
- Better error handling

#### 1.3 Command Pattern with CQRS
**Priority: MEDIUM**

Separate commands (state changes) from queries (data retrieval):

```python
from dataclasses import dataclass
from abc import ABC, abstractmethod

# Commands (write operations)
@dataclass
class RollDiceCommand:
    user_id: str
    num_dice: int
    explode: bool
    target_number: Optional[int]

class CommandHandler(ABC):
    @abstractmethod
    async def handle(self, command) -> CommandResult:
        pass

class RollDiceCommandHandler(CommandHandler):
    def __init__(
        self, 
        dice_service: DiceService,
        user_repo: UserDataRepository,
        event_publisher: EventPublisher
    ):
        self.dice_service = dice_service
        self.user_repo = user_repo
        self.event_publisher = event_publisher
    
    async def handle(self, command: RollDiceCommand) -> CommandResult:
        result = self.dice_service.roll_dice(
            command.num_dice,
            command.explode,
            command.target_number
        )
        
        # Save to history
        await self.user_repo.add_roll_history(command.user_id, result)
        
        # Publish event
        await self.event_publisher.publish(DiceRolledEvent(result))
        
        return CommandResult(success=True, data=result)

# Queries (read operations)
@dataclass
class GetRollHistoryQuery:
    user_id: str
    limit: int = 10

class QueryHandler(ABC):
    @abstractmethod
    async def handle(self, query) -> QueryResult:
        pass

class GetRollHistoryQueryHandler(QueryHandler):
    def __init__(self, user_repo: UserDataRepository):
        self.user_repo = user_repo
    
    async def handle(self, query: GetRollHistoryQuery) -> QueryResult:
        history = await self.user_repo.get_roll_history(
            query.user_id, 
            query.limit
        )
        return QueryResult(success=True, data=history)
```

**Benefits:**
- Clear responsibility separation
- Easier to optimize queries independently
- Better testability
- Event sourcing ready

#### 1.4 Dependency Injection Container
**Priority: HIGH**

Use a DI container to manage dependencies:

```python
from dependency_injector import containers, providers

class Container(containers.DeclarativeContainer):
    config = providers.Singleton(Config.load)
    
    # Infrastructure
    database = providers.Singleton(
        Database.connect,
        mongodb_url=config.provided.mongodb_url
    )
    
    encryptor = providers.Singleton(
        Encryptor,
        key=config.provided.crypto_key,
        iv=config.provided.crypto_iv
    )
    
    cache = providers.Singleton(Cache)
    
    # Repositories
    user_data_repository = providers.Factory(
        MongoUserDataRepository,
        db=database,
        encryptor=encryptor,
        cache=cache
    )
    
    # Services
    dice_service = providers.Factory(DiceService)
    
    # Command Handlers
    roll_dice_handler = providers.Factory(
        RollDiceCommandHandler,
        dice_service=dice_service,
        user_repo=user_data_repository
    )

# Usage
container = Container()
handler = container.roll_dice_handler()
```

**Benefits:**
- Centralized dependency management
- Easy to swap implementations for testing
- Lifecycle management
- Configuration validation

---

## 2. Code Quality & Maintainability

### Current Issues
- **Lack of type hints**: Makes code hard to understand
- **Long functions**: Some functions >100 lines
- **No docstrings**: Missing documentation
- **Magic numbers**: Hardcoded values throughout
- **Inconsistent naming**: Mixed conventions

### Recommended Improvements

#### 2.1 Strict Type Checking with mypy
**Priority: HIGH**

```python
# pyproject.toml
[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_any_generics = true
check_untyped_defs = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true

# Example typed code
from typing import Protocol, TypeAlias, Literal

DiceType: TypeAlias = Literal["d6", "d10"]
GameSystem: TypeAlias = Literal["sr1e", "sr2e", "sr3e", "cp2020", "cpr"]

class RollResult(Protocol):
    rolls: list[int]
    successes: int
    total: int

def roll_dice(
    num_dice: int,
    dice_type: DiceType = "d6",
    explode: bool = False,
    target_number: int | None = None
) -> RollResult:
    """Roll dice with optional exploding and target number.
    
    Args:
        num_dice: Number of dice to roll (1-100)
        dice_type: Type of dice ("d6" or "d10")
        explode: Whether to use exploding dice (Rule of 6)
        target_number: Minimum value for success, None for no counting
        
    Returns:
        RollResult containing rolls, successes, and total
        
    Raises:
        ValueError: If num_dice is out of range
        
    Examples:
        >>> result = roll_dice(5, explode=True, target_number=4)
        >>> print(f"Rolled {result.successes} successes")
    """
    if not 1 <= num_dice <= 100:
        raise ValueError(f"num_dice must be 1-100, got {num_dice}")
    
    # Implementation
```

#### 2.2 Code Linting and Formatting
**Priority: HIGH**

```toml
# pyproject.toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
    "ARG", # flake8-unused-arguments
    "SIM", # flake8-simplify
]

[tool.black]
line-length = 100
target-version = ["py311"]

[tool.isort]
profile = "black"
line_length = 100
```

#### 2.3 Function Decomposition
**Priority: MEDIUM**

Break long functions into smaller, focused ones:

**Before:**
```python
async def handle_message(message):
    # 150 lines of command parsing, validation, execution, and response
    if message.content.startswith('!'):
        cmd = message.content[1:].split()[0]
        if cmd.isdigit():
            # 50 lines of dice rolling logic
        elif cmd == 'init':
            # 30 lines of initiative logic
        elif cmd == 'save':
            # 40 lines of macro saving logic
        # ... more command handling
```

**After:**
```python
async def handle_message(message: discord.Message) -> None:
    """Route message to appropriate command handler."""
    if not message.content.startswith('!'):
        return
    
    command = parse_command(message.content)
    handler = get_command_handler(command.name)
    
    if handler:
        await handler.execute(message, command)

def parse_command(content: str) -> Command:
    """Parse command from message content."""
    parts = content[1:].split()
    return Command(name=parts[0], args=parts[1:])

def get_command_handler(name: str) -> Optional[CommandHandler]:
    """Get appropriate handler for command name."""
    return COMMAND_REGISTRY.get(name.lower())
```

#### 2.4 Constants and Configuration
**Priority: MEDIUM**

Centralize magic numbers and strings:

```python
# constants.py
from enum import Enum

class DiceConstants:
    MIN_DICE = 1
    MAX_DICE = 100
    MAX_EXPLODE_DEPTH = 50  # Prevent infinite recursion
    
class MessageLimits:
    DISCORD_MAX_LENGTH = 2000
    EMBED_TITLE_MAX = 256
    EMBED_DESCRIPTION_MAX = 4096
    EMBED_FIELD_MAX = 1024
    
class CacheConfig:
    DEFAULT_TTL = 3600  # 1 hour
    MAX_CACHE_SIZE = 10000
    EVICTION_POLICY = "LRU"

class GameSystem(Enum):
    SHADOWRUN_1E = "sr1e"
    SHADOWRUN_2E = "sr2e"
    SHADOWRUN_3E = "sr3e"
    CYBERPUNK_2020 = "cp2020"
    CYBERPUNK_RED = "cpr"
    
    @property
    def uses_d6(self) -> bool:
        return self in {self.SHADOWRUN_1E, self.SHADOWRUN_2E, self.SHADOWRUN_3E}
    
    @property
    def uses_d10(self) -> bool:
        return self in {self.CYBERPUNK_2020, self.CYBERPUNK_RED}
```

---

## 3. Testing Strategy

### Current Issues
- **No automated tests**: Cannot refactor safely
- **No test coverage**: Unknown code quality
- **Manual testing only**: Time-consuming and error-prone
- **Hard to test**: Tight coupling prevents unit testing

### Recommended Improvements

#### 3.1 Comprehensive Test Suite
**Priority: CRITICAL**

```python
# tests/unit/test_dice_roller.py
import pytest
from src.domain.services.dice_service import DiceService
from src.domain.entities.dice_result import DiceResult

class TestDiceService:
    @pytest.fixture
    def dice_service(self):
        return DiceService()
    
    def test_roll_basic_dice(self, dice_service):
        result = dice_service.roll_dice(5, explode=False)
        
        assert len(result.rolls) == 5
        assert all(1 <= roll <= 6 for roll in result.rolls)
        assert result.total == sum(result.rolls)
    
    def test_roll_with_target_number(self, dice_service):
        result = dice_service.roll_dice(10, explode=False, target_number=4)
        
        expected_successes = sum(1 for roll in result.rolls if roll >= 4)
        assert result.successes == expected_successes
    
    @pytest.mark.parametrize("num_dice,explode,tn", [
        (1, False, None),
        (5, True, 4),
        (10, False, 3),
        (20, True, 5),
    ])
    def test_roll_variations(self, dice_service, num_dice, explode, tn):
        result = dice_service.roll_dice(num_dice, explode, tn)
        assert len(result.rolls) >= num_dice  # >= because of exploding
    
    def test_invalid_dice_count_raises_error(self, dice_service):
        with pytest.raises(ValueError, match="num_dice must be"):
            dice_service.roll_dice(0)
        
        with pytest.raises(ValueError):
            dice_service.roll_dice(101)

# tests/integration/test_roll_command.py
import pytest
from unittest.mock import AsyncMock, Mock
from src.application.commands.roll_dice_handler import RollDiceCommandHandler

@pytest.mark.asyncio
class TestRollDiceCommand:
    @pytest.fixture
    def mock_dice_service(self):
        service = Mock()
        service.roll_dice.return_value = Mock(
            rolls=[6, 5, 4],
            successes=3,
            total=15
        )
        return service
    
    @pytest.fixture
    def mock_repository(self):
        repo = AsyncMock()
        return repo
    
    @pytest.fixture
    def handler(self, mock_dice_service, mock_repository):
        return RollDiceCommandHandler(mock_dice_service, mock_repository)
    
    async def test_successful_roll(self, handler):
        command = RollDiceCommand(
            user_id="123",
            num_dice=5,
            explode=True,
            target_number=4
        )
        
        result = await handler.handle(command)
        
        assert result.success
        assert result.data.successes == 3
```

#### 3.2 Test Coverage Requirements
**Priority: HIGH**

```toml
# pyproject.toml
[tool.coverage.run]
source = ["src"]
omit = ["*/tests/*", "*/migrations/*"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
]
fail_under = 80  # Require 80% coverage minimum
```

**Coverage Goals:**
- Domain logic: 95%+
- Application layer: 90%+
- Infrastructure: 75%+
- Overall: 80%+

#### 3.3 Property-Based Testing
**Priority: MEDIUM**

Use Hypothesis for comprehensive testing:

```python
from hypothesis import given, strategies as st

@given(
    num_dice=st.integers(min_value=1, max_value=100),
    target_number=st.integers(min_value=1, max_value=6)
)
def test_dice_properties(num_dice, target_number):
    """Test properties that should always hold for dice rolls."""
    result = roll_dice(num_dice, explode=False, target_number=target_number)
    
    # Property: Number of rolls should equal num_dice
    assert len(result.rolls) == num_dice
    
    # Property: All rolls should be in valid range
    assert all(1 <= roll <= 6 for roll in result.rolls)
    
    # Property: Successes should never exceed number of dice
    assert result.successes <= num_dice
    
    # Property: Total should equal sum of rolls
    assert result.total == sum(result.rolls)
```

#### 3.4 Integration Tests with Test Containers
**Priority: MEDIUM**

```python
import pytest
from testcontainers.mongodb import MongoDbContainer

@pytest.fixture(scope="session")
def mongodb_container():
    with MongoDbContainer("mongo:6.0") as mongo:
        yield mongo

@pytest.fixture
async def test_database(mongodb_container):
    db = await Database.connect(mongodb_container.get_connection_url())
    yield db
    await Database.close()

@pytest.mark.integration
async def test_user_data_persistence(test_database):
    repo = MongoUserDataRepository(test_database, encryptor, cache)
    
    # Save data
    await repo.save_user_data(UserData(
        server_id="123",
        channel_id="456",
        user_id="789",
        macros=["attack: 8! tn4"]
    ))
    
    # Retrieve data
    data = await repo.get_user_data("123", "456", "789")
    
    assert data is not None
    assert len(data.macros) == 1
```

---

## 4. Performance Optimization

### Current Issues
- **N+1 queries**: Multiple database calls in loops
- **No connection pooling**: New connections for each query
- **Inefficient caching**: Cache everything or nothing
- **Synchronous operations**: Blocking calls in async context
- **No query optimization**: Missing database indexes

### Recommended Improvements

#### 4.1 Database Indexing Strategy
**Priority: HIGH**

```python
async def create_indexes(db: Database) -> None:
    """Create database indexes for optimal query performance."""
    
    # Folder lookups (server/channel/user hierarchy)
    await db.folders.create_index([
        ("parent", 1),
        ("name", 1)
    ], unique=True)
    
    # String lookups (files in folders)
    await db.strings.create_index([
        ("parent", 1),
        ("name", 1)
    ], unique=True)
    
    # Reminder queries
    await db.reminders.create_index([
        ("scheduled_time", 1),
        ("status", 1)
    ])
    
    # User data lookups with compound index
    await db.folders.create_index([
        ("encrypted", 1),
        ("parent", 1)
    ])
```

#### 4.2 Smart Caching with TTL
**Priority: HIGH**

```python
from datetime import datetime, timedelta
from typing import Optional, TypeVar, Generic
from dataclasses import dataclass

T = TypeVar('T')

@dataclass
class CacheEntry(Generic[T]):
    value: T
    expires_at: datetime
    hit_count: int = 0
    
    def is_expired(self) -> bool:
        return datetime.now() > self.expires_at

class SmartCache:
    def __init__(self, max_size: int = 10000, default_ttl: int = 3600):
        self._cache: dict[str, CacheEntry] = {}
        self._max_size = max_size
        self._default_ttl = default_ttl
        self._hits = 0
        self._misses = 0
    
    def get(self, key: str) -> Optional[any]:
        if key not in self._cache:
            self._misses += 1
            return None
        
        entry = self._cache[key]
        
        if entry.is_expired():
            del self._cache[key]
            self._misses += 1
            return None
        
        entry.hit_count += 1
        self._hits += 1
        return entry.value
    
    def set(
        self, 
        key: str, 
        value: any, 
        ttl: Optional[int] = None
    ) -> None:
        if len(self._cache) >= self._max_size:
            self._evict_lru()
        
        expires_at = datetime.now() + timedelta(
            seconds=ttl or self._default_ttl
        )
        self._cache[key] = CacheEntry(value=value, expires_at=expires_at)
    
    def _evict_lru(self) -> None:
        """Evict least recently used entries."""
        sorted_entries = sorted(
            self._cache.items(),
            key=lambda x: x[1].hit_count
        )
        # Remove bottom 10%
        to_remove = max(1, len(sorted_entries) // 10)
        for key, _ in sorted_entries[:to_remove]:
            del self._cache[key]
    
    @property
    def hit_rate(self) -> float:
        total = self._hits + self._misses
        return self._hits / total if total > 0 else 0.0
```

#### 4.3 Batch Operations
**Priority: MEDIUM**

```python
async def get_multiple_user_data(
    user_ids: list[str],
    server_id: str,
    channel_id: str
) -> dict[str, UserData]:
    """Fetch multiple user data in one query."""
    
    # Build cache keys
    cache_keys = [
        f"{server_id}:{channel_id}:{uid}" for uid in user_ids
    ]
    
    # Check cache first
    results = {}
    uncached_ids = []
    
    for uid, cache_key in zip(user_ids, cache_keys):
        if cached := cache.get(cache_key):
            results[uid] = cached
        else:
            uncached_ids.append(uid)
    
    # Fetch uncached in one query
    if uncached_ids:
        db_results = await db.folders.find({
            "parent": channel_folder_id,
            "name": {"$in": [encrypt(uid) for uid in uncached_ids]}
        }).to_list(length=len(uncached_ids))
        
        # Process and cache results
        for doc in db_results:
            user_id = decrypt(doc["name"])
            user_data = await load_user_data(doc["_id"])
            results[user_id] = user_data
            cache.set(f"{server_id}:{channel_id}:{user_id}", user_data)
    
    return results
```

#### 4.4 Async Optimization
**Priority: HIGH**

```python
import asyncio

async def roll_initiative_for_all(
    players: list[Player],
    npcs: list[NPC]
) -> InitiativeOrder:
    """Roll initiative for all combatants in parallel."""
    
    # Create coroutines for each roll
    player_rolls = [
        roll_initiative(p.dice, p.modifier) 
        for p in players
    ]
    npc_rolls = [
        roll_initiative(n.dice, n.modifier) 
        for n in npcs
    ]
    
    # Execute all rolls concurrently
    player_results, npc_results = await asyncio.gather(
        asyncio.gather(*player_rolls),
        asyncio.gather(*npc_rolls)
    )
    
    # Combine and sort
    return create_initiative_order(
        zip(players, player_results),
        zip(npcs, npc_results)
    )
```

#### 4.5 Connection Pooling
**Priority: HIGH**

```python
from motor.motor_asyncio import AsyncIOMotorClient

class Database:
    @classmethod
    async def connect(
        cls,
        mongodb_url: str,
        db_name: str = "sr1egamebot",
        pool_size: int = 50,
        max_idle_time_ms: int = 30000
    ) -> 'Database':
        cls._client = AsyncIOMotorClient(
            mongodb_url,
            maxPoolSize=pool_size,
            minPoolSize=10,
            maxIdleTimeMS=max_idle_time_ms,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000,
            retryWrites=True,
            retryReads=True
        )
        
        cls._db = cls._client[db_name]
        
        # Verify connection
        await cls._client.admin.command('ping')
        logger.info(f"Connected to MongoDB with pool size {pool_size}")
        
        return cls()
```

---

## 5. Observability & Monitoring

### Current Issues
- **Limited logging**: Only basic winston logs
- **No metrics**: Can't track performance
- **No tracing**: Can't debug slow operations
- **No health checks**: Unknown system status
- **No alerting**: Problems discovered too late

### Recommended Improvements

#### 5.1 Structured Logging
**Priority: HIGH**

```python
import structlog
from typing import Any

# Configure structured logging
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True
)

logger = structlog.get_logger()

# Usage with context
async def roll_dice_command(user_id: str, num_dice: int) -> None:
    log = logger.bind(
        user_id=user_id,
        command="roll_dice",
        num_dice=num_dice
    )
    
    log.info("rolling_dice")
    
    try:
        result = await dice_service.roll(num_dice)
        log.info("dice_rolled", successes=result.successes)
    except Exception as e:
        log.error("roll_failed", error=str(e), exc_info=True)
        raise
```

#### 5.2 Metrics Collection
**Priority: HIGH**

```python
from prometheus_client import Counter, Histogram, Gauge
import time

# Define metrics
command_counter = Counter(
    'bot_commands_total',
    'Total commands executed',
    ['command_name', 'status']
)

command_duration = Histogram(
    'bot_command_duration_seconds',
    'Command execution time',
    ['command_name']
)

active_games = Gauge(
    'bot_active_games',
    'Number of active game sessions'
)

database_operations = Histogram(
    'bot_database_operation_seconds',
    'Database operation duration',
    ['operation']
)

# Usage
async def execute_command(command: Command) -> None:
    start_time = time.time()
    
    try:
        await command.execute()
        command_counter.labels(
            command_name=command.name,
            status='success'
        ).inc()
    except Exception as e:
        command_counter.labels(
            command_name=command.name,
            status='error'
        ).inc()
        raise
    finally:
        duration = time.time() - start_time
        command_duration.labels(
            command_name=command.name
        ).observe(duration)
```

#### 5.3 Distributed Tracing
**Priority: MEDIUM**

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter

# Configure tracing
trace.set_tracer_provider(TracerProvider())
jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)

tracer = trace.get_tracer(__name__)

# Usage
async def handle_roll_command(ctx: Context) -> None:
    with tracer.start_as_current_span("handle_roll_command") as span:
        span.set_attribute("user.id", ctx.user_id)
        span.set_attribute("command", "roll")
        
        with tracer.start_as_current_span("parse_command"):
            command = parse_command(ctx.message)
        
        with tracer.start_as_current_span("roll_dice"):
            result = await dice_service.roll(command.num_dice)
        
        with tracer.start_as_current_span("send_response"):
            await ctx.send(format_result(result))
```

#### 5.4 Health Checks
**Priority: HIGH**

```python
from dataclasses import dataclass
from enum import Enum

class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"

@dataclass
class HealthCheck:
    status: HealthStatus
    checks: dict[str, bool]
    response_time_ms: float

class HealthMonitor:
    async def check_health(self) -> HealthCheck:
        start = time.time()
        
        checks = {
            "database": await self._check_database(),
            "discord": await self._check_discord(),
            "cache": self._check_cache()
        }
        
        # Determine overall status
        if all(checks.values()):
            status = HealthStatus.HEALTHY
        elif any(checks.values()):
            status = HealthStatus.DEGRADED
        else:
            status = HealthStatus.UNHEALTHY
        
        duration_ms = (
