# SR1eGameBot - Python Migration Guide

## Document Information
- **Original**: JavaScript/Node.js implementation
- **Target**: Python 3.10+ implementation
- **Date**: November 2025
- **Audience**: Junior Python Developers

---

## 1. Migration Overview

### 1.1 Purpose
This guide provides a complete roadmap for rewriting SR1eGameBot from JavaScript/Node.js to Python, maintaining 100% feature parity while leveraging Python's strengths.

### 1.2 Technology Stack Changes

| Component | JavaScript | Python |
|-----------|-----------|--------|
| Runtime | Node.js | Python 3.10+ |
| Discord Library | discord.js v14 | discord.py v2.3+ |
| Database Driver | mongodb (Node) | motor (async) or pymongo |
| Logging | winston | logging (built-in) |
| Environment | dotenv | python-dotenv |
| Async | Promises/async-await | asyncio/async-await |
| Encryption | crypto (built-in) | cryptography |

### 1.3 Key Benefits of Python Migration
- Stronger type hints with Python 3.10+
- Better built-in libraries (logging, datetime)
- More readable code for complex logic
- Better debugging tools
- Easier testing with pytest
- Native async/await support

---

## 2. Project Structure

### 2.1 Directory Layout

```
sr1egamebot-python/
├── src/
│   ├── __init__.py
│   ├── main.py                    # Entry point
│   ├── bot.py                     # Discord bot setup
│   ├── config.py                  # Configuration management
│   ├── database/
│   │   ├── __init__.py
│   │   ├── db.py                  # Database connection
│   │   ├── models.py              # Data models
│   │   └── cache.py               # Caching layer
│   ├── commands/
│   │   ├── __init__.py
│   │   ├── base.py                # Base command class
│   │   ├── dice.py                # Dice rolling commands
│   │   ├── initiative.py          # Initiative system
│   │   ├── macro.py               # Macro commands
│   │   ├── scene.py               # Scene management
│   │   ├── gmscreen.py            # GM screen commands
│   │   ├── reminder.py            # Reminder system
│   │   ├── ammo.py                # Ammo tracking
│   │   └── admin.py               # Admin commands
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── dice_roller.py         # Dice rolling logic
│   │   ├── encryption.py          # Encryption utilities
│   │   ├── logger.py              # Logging setup
│   │   └── helpers.py             # Helper functions
│   └── migrations/
│       ├── __init__.py
│       └── migrate_from_js.py     # Migration from JS version
├── tests/
│   ├── __init__.py
│   ├── test_dice.py
│   ├── test_initiative.py
│   ├── test_database.py
│   └── test_commands.py
├── .env.example
├── .gitignore
├── requirements.txt
├── setup.py
├── README.md
└── Dockerfile (optional)
```

---

## 3. Core Concepts Translation

### 3.1 Async/Await Pattern

**JavaScript:**
```javascript
async function handleRollCommand(msg, cmd, args) {
  const result = await rollDice(numDice, explode, tn);
  await msg.channel.send(output);
}
```

**Python:**
```python
async def handle_roll_command(msg: discord.Message, cmd: str, args: list[str]) -> None:
    result = await roll_dice(num_dice, explode, tn)
    await msg.channel.send(output)
```

### 3.2 Database Operations

**JavaScript (MongoDB):**
```javascript
const doc = await Database.getTable("strings").findOne({
  $and: [{name: filename}, {parent: ObjectId(parentID)}]
});
```

**Python (Motor - Async):**
```python
doc = await db.strings.find_one({
    "$and": [{"name": filename}, {"parent": ObjectId(parent_id)}]
})
```

### 3.3 Event Handling

**JavaScript:**
```javascript
bot.on('messageCreate', (msg) => {
    handleMessage(msg);
});
```

**Python:**
```python
@bot.event
async def on_message(message: discord.Message) -> None:
    await handle_message(message)
```

---

## 4. Implementation Guidelines

### 4.1 Code Style
- Follow PEP 8 style guide
- Use type hints throughout (Python 3.10+ syntax)
- Use dataclasses for data structures
- Use enums for constants
- Maximum line length: 100 characters
- Use docstrings (Google style)

### 4.2 Naming Conventions

| Type | JavaScript | Python |
|------|-----------|--------|
| Variables | camelCase | snake_case |
| Functions | camelCase | snake_case |
| Classes | PascalCase | PascalCase |
| Constants | UPPER_CASE | UPPER_CASE |
| Private | _prefix | _prefix or __prefix |

### 4.3 Error Handling

**JavaScript:**
```javascript
try {
    await someOperation();
} catch (e) {
    logError(e);
}
```

**Python:**
```python
try:
    await some_operation()
except Exception as e:
    logger.error(f"Operation failed: {e}", exc_info=True)
```

---

## 5. Module-by-Module Migration

### 5.1 Main Entry Point (`main.py`)

**Key Responsibilities:**
- Load configuration
- Initialize logging
- Connect to MongoDB
- Initialize Discord bot
- Register command handlers
- Start event loop

**Implementation Pattern:**
```python
import asyncio
import discord
from discord.ext import commands
from src.config import Config
from src.database.db import Database
from src.utils.logger import setup_logging

async def main():
    # Setup
    config = Config.load()
    setup_logging(config.log_level)
    
    # Database
    db = await Database.connect(config.mongodb_url)
    
    # Bot
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix='!', intents=intents)
    
    # Load commands
    await bot.load_extension('src.commands.dice')
    # ... load other extensions
    
    # Start
    await bot.start(config.discord_token)

if __name__ == "__main__":
    asyncio.run(main())
```

### 5.2 Configuration (`config.py`)

**Features:**
- Load from environment variables
- Load from .env file
- Validation
- Type safety

**Implementation:**
```python
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import os
from dotenv import load_dotenv

@dataclass
class Config:
    discord_token: str
    mongodb_url: str
    crypto_key: bytes
    crypto_iv: bytes
    log_level: str = "INFO"
    
    @classmethod
    def load(cls, env_file: Optional[Path] = None) -> 'Config':
        if env_file:
            load_dotenv(env_file)
        
        return cls(
            discord_token=os.getenv('DISCORD_TOKEN', ''),
            mongodb_url=os.getenv('MONGODB_URL', ''),
            crypto_key=bytes.fromhex(os.getenv('CRYPTO_KEY', '')),
            crypto_iv=bytes.fromhex(os.getenv('CRYPTO_IV', '')),
            log_level=os.getenv('LOG_LEVEL', 'INFO')
        )
    
    def validate(self) -> None:
        if not self.discord_token:
            raise ValueError("DISCORD_TOKEN is required")
        if not self.mongodb_url:
            raise ValueError("MONGODB_URL is required")
```

### 5.3 Database Layer (`database/db.py`)

**Features:**
- Async MongoDB connection (Motor)
- Connection pooling
- Automatic reconnection
- Type-safe queries

**Implementation Pattern:**
```python
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class Database:
    _client: Optional[AsyncIOMotorClient] = None
    _db: Optional[AsyncIOMotorDatabase] = None
    
    @classmethod
    async def connect(cls, mongodb_url: str, db_name: str = "sr1egamebot") -> 'Database':
        try:
            cls._client = AsyncIOMotorClient(mongodb_url)
            cls._db = cls._client[db_name]
            # Test connection
            await cls._client.admin.command('ping')
            logger.info("Connected to MongoDB")
            return cls()
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    @property
    def folders(self):
        return self._db.folders
    
    @property
    def strings(self):
        return self._db.strings
    
    @classmethod
    async def close(cls) -> None:
        if cls._client:
            cls._client.close()
            logger.info("MongoDB connection closed")
```

### 5.4 Caching Layer (`database/cache.py`)

**Purpose:** In-memory caching to reduce database queries

**Implementation:**
```python
from dataclasses import dataclass, field
from typing import Optional, Dict, List
from bson import ObjectId

@dataclass
class CacheEntry:
    db_id: str
    discord_id: str
    parent_id: Optional[str] = None

@dataclass
class Cache:
    servers: Dict[str, CacheEntry] = field(default_factory=dict)
    channels: Dict[str, CacheEntry] = field(default_factory=dict)
    users: Dict[str, CacheEntry] = field(default_factory=dict)
    files: Dict[str, CacheEntry] = field(default_factory=dict)
    file_contents: Dict[str, str] = field(default_factory=dict)
    play_channels: Dict[str, str] = field(default_factory=dict)
    
    def get_server(self, discord_id: str) -> Optional[CacheEntry]:
        return self.servers.get(discord_id)
    
    def set_server(self, discord_id: str, db_id: str) -> None:
        self.servers[discord_id] = CacheEntry(db_id=db_id, discord_id=discord_id)
    
    def clear(self) -> None:
        self.servers.clear()
        self.channels.clear()
        self.users.clear()
        self.files.clear()
        self.file_contents.clear()
        self.play_channels.clear()

# Global cache instance
cache = Cache()
```

### 5.5 Encryption Utilities (`utils/encryption.py`)

**Features:**
- AES-256-CBC encryption
- Decrypt/encrypt helpers
- Type-safe interfaces

**Implementation:**
```python
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from typing import Union
import logging

logger = logging.getLogger(__name__)

class Encryptor:
    def __init__(self, key: bytes, iv: bytes):
        self.key = key
        self.iv = iv
        self.backend = default_backend()
    
    def encrypt(self, plaintext: str) -> str:
        try:
            cipher = Cipher(
                algorithms.AES(self.key),
                modes.CBC(self.iv),
                backend=self.backend
            )
            encryptor = cipher.encryptor()
            
            # Pad plaintext to block size
            padded = self._pad(plaintext.encode('utf-8'))
            ciphertext = encryptor.update(padded) + encryptor.finalize()
            
            return ciphertext.hex()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise
    
    def decrypt(self, ciphertext: str) -> str:
        try:
            cipher = Cipher(
                algorithms.AES(self.key),
                modes.CBC(self.iv),
                backend=self.backend
            )
            decryptor = cipher.decryptor()
            
            padded = decryptor.update(bytes.fromhex(ciphertext)) + decryptor.finalize()
            plaintext = self._unpad(padded)
            
            return plaintext.decode('utf-8')
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise
    
    @staticmethod
    def _pad(data: bytes, block_size: int = 16) -> bytes:
        padding_length = block_size - (len(data) % block_size)
        padding = bytes([padding_length] * padding_length)
        return data + padding
    
    @staticmethod
    def _unpad(data: bytes) -> bytes:
        padding_length = data[-1]
        return data[:-padding_length]
```

### 5.6 Dice Rolling System (`utils/dice_roller.py`)

**Features:**
- D6 and D10 support
- Exploding dice (Rule of 6)
- Target number checks
- Opposed rolls

**Implementation:**
```python
import random
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class DiceResult:
    rolls: List[int]
    successes: int
    total: int

class DiceRoller:
    @staticmethod
    def roll_d6(explode: bool = False) -> int:
        roll = random.randint(1, 6)
        if roll == 6 and explode:
            roll += DiceRoller.roll_d6(explode=True)
        return roll
    
    @staticmethod
    def roll_d10() -> int:
        return random.randint(1, 10)
    
    @staticmethod
    def roll_dice(
        num_dice: int,
        explode: bool = False,
        target_number: int = -1,
        dice_type: str = 'd6'
    ) -> DiceResult:
        rolls = []
        
        for _ in range(num_dice):
            if dice_type == 'd6':
                roll = DiceRoller.roll_d6(explode)
            else:  # d10
                roll = DiceRoller.roll_d10()
            rolls.append(roll)
        
        # Sort descending for readability
        rolls.sort(reverse=True)
        
        # Count successes if TN provided
        successes = 0
        if target_number > 0:
            successes = sum(1 for roll in rolls if roll >= target_number)
        
        return DiceResult(
            rolls=rolls,
            successes=successes,
            total=sum(rolls)
        )
    
    @staticmethod
    def opposed_roll(
        attacker_dice: int,
        attacker_tn: int,
        attacker_explode: bool,
        defender_dice: int,
        defender_tn: int,
        defender_explode: bool
    ) -> Tuple[DiceResult, DiceResult, int]:
        attacker_result = DiceRoller.roll_dice(
            attacker_dice, attacker_explode, attacker_tn
        )
        defender_result = DiceRoller.roll_dice(
            defender_dice, defender_explode, defender_tn
        )
        
        net_successes = attacker_result.successes - defender_result.successes
        
        return attacker_result, defender_result, net_successes
```

### 5.7 Command Parser (`utils/helpers.py`)

**Features:**
- Parse dice commands
- Extract target numbers
- Parse opposed rolls
- Handle modifiers

**Implementation:**
```python
import re
from typing import Optional, Tuple, List

class CommandParser:
    @staticmethod
    def parse_tn(args: List[str]) -> int:
        """Extract target number from arguments."""
        for i, arg in enumerate(args):
            if arg.lower().startswith('tn'):
                # Check if TN is attached (tn4) or separate (tn 4)
                if len(arg) > 2:
                    tn_str = arg[2:]
                    if tn_str.isdigit():
                        return int(tn_str)
                elif i + 1 < len(args) and args[i + 1].isdigit():
                    return int(args[i + 1])
        return -1
    
    @staticmethod
    def parse_modifier(args: List[str]) -> int:
        """Extract modifier (+5 or -3) from arguments."""
        for arg in args:
            if arg.startswith(('+', '-')) and arg[1:].isdigit():
                return int(arg)
        return 0
    
    @staticmethod
    def parse_opposed(args: List[str]) -> Tuple[bool, int, int, bool]:
        """
        Parse opposed roll arguments.
        Returns: (is_opposed, opponent_dice, opponent_tn, opponent_explode)
        """
        is_opposed = False
        opponent_dice = -1
        opponent_tn = -1
        opponent_explode = False
        
        for i, arg in enumerate(args):
            if arg.lower().startswith('vs'):
                is_opposed = True
                vs_part = arg[2:]
                
                if vs_part.endswith('!'):
                    opponent_explode = True
                    vs_part = vs_part[:-1]
                
                if vs_part.isdigit():
                    opponent_dice = int(vs_part)
            
            elif arg.lower().startswith('otn'):
                otn_part = arg[3:]
                if otn_part.isdigit():
                    opponent_tn = int(otn_part)
                elif i + 1 < len(args) and args[i + 1].isdigit():
                    opponent_tn = int(args[i + 1])
        
        return is_opposed, opponent_dice, opponent_tn, opponent_explode
```

---

## 6. Command Implementation Examples

### 6.1 Dice Command (`commands/dice.py`)

```python
import discord
from discord.ext import commands
from typing import Optional
import logging
from src.utils.dice_roller import DiceRoller
from src.utils.helpers import CommandParser

logger = logging.getLogger(__name__)

class DiceCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Ignore bot messages
        if message.author.bot:
            return
        
        # Check if message starts with !
        if not message.content.startswith('!'):
            return
        
        # Parse command
        parts = message.content[1:].split()
        if not parts:
            return
        
        cmd = parts[0].lower()
        args = parts[1:]
        
        # Check if it's a dice command
        await self.handle_roll(message, cmd, args)
    
    async def handle_roll(
        self,
        message: discord.Message,
        cmd: str,
        args: list[str]
    ) -> None:
        """Handle dice roll commands."""
        # Parse command format
        explode = cmd.endswith('!')
        is_total = cmd.endswith('t')
        
        # Extract number of dice
        if explode:
            num_dice_str = cmd[:-1]
        elif is_total:
            num_dice_str = cmd[:-1]
        else:
            num_dice_str = cmd
        
        if not num_dice_str.isdigit():
            return  # Not a dice command
        
        num_dice = int(num_dice_str)
        
        # Parse options
        tn = CommandParser.parse_tn(args)
        modifier = CommandParser.parse_modifier(args) if is_total else 0
        is_opposed, opp_dice, opp_tn, opp_explode = CommandParser.parse_opposed(args)
        
        # Roll dice
        if is_opposed:
            await self.handle_opposed_roll(
                message, num_dice, tn, explode,
                opp_dice, opp_tn, opp_explode, args
            )
        elif is_total:
            await self.handle_total_roll(
                message, num_dice, modifier, args
            )
        else:
            await self.handle_standard_roll(
                message, num_dice, tn, explode, args
            )
    
    async def handle_standard_roll(
        self,
        message: discord.Message,
        num_dice: int,
        tn: int,
        explode: bool,
        args: list[str]
    ) -> None:
        """Handle standard dice roll."""
        result = DiceRoller.roll_dice(num_dice, explode, tn)
        
        # Format output
        note = ' '.join(args) if args else ''
        if note:
            note = f"({note})"
        
        if tn > 0:
            output = (
                f"{message.author.mention}, you rolled "
                f"{result.successes} successes "
                f"({', '.join(map(str, result.rolls))}) {note}"
            )
        else:
            output = (
                f"{message.author.mention}, you rolled "
                f"({', '.join(map(str, result.rolls))}) {note}"
            )
        
        await message.channel.send(output)
        await message.add_reaction('🎲')
    
    async def handle_total_roll(
        self,
        message: discord.Message,
        num_dice: int,
        modifier: int,
        args: list[str]
    ) -> None:
        """Handle totaled dice roll."""
        result = DiceRoller.roll_dice(num_dice, False, -1)
        total = result.total + modifier
        
        note = ' '.join(args) if args else ''
        if note:
            note = f"({note})"
        
        mod_text = f" {modifier:+d}" if modifier != 0 else ""
        output = (
            f"{message.author.mention}, you rolled "
            f"[Total: {total}] | "
            f"({', '.join(map(str, result.rolls))}{mod_text}) {note}"
        )
        
        await message.channel.send(output)
        await message.add_reaction('🎲')
    
    async def handle_opposed_roll(
        self,
        message: discord.Message,
        att_dice: int,
        att_tn: int,
        att_explode: bool,
        def_dice: int,
        def_tn: int,
        def_explode: bool,
        args: list[str]
    ) -> None:
        """Handle opposed roll."""
        att_result, def_result, net = DiceRoller.opposed_roll(
            att_dice, att_tn, att_explode,
            def_dice, def_tn, def_explode
        )
        
        note = ' '.join(args) if args else ''
        if note:
            note = f"({note})"
        
        if net > 0:
            outcome = f"{net} net successes"
        elif net == 0:
            outcome = "0 net successes"
        else:
            outcome = f"{abs(net)} *fewer* successes than opponent"
        
        output = (
            f"{message.author.mention}, you rolled {outcome} | "
            f"({', '.join(map(str, att_result.rolls))}) vs "
            f"({', '.join(map(str, def_result.rolls))}) {note}"
        )
        
        await message.channel.send(output)
        await message.add_reaction('🎲')

async def setup(bot: commands.Bot):
    await bot.add_cog(DiceCommands(bot))
```

---

## 7. Testing Strategy

### 7.1 Unit Tests

**Example: `tests/test_dice.py`**

```python
import pytest
from src.utils.dice_roller import DiceRoller, DiceResult

def test_roll_d6_basic():
    result = DiceRoller.roll_d6(explode=False)
    assert 1 <= result <= 6

def test_roll_d6_exploding():
    # Run multiple times to test exploding
    results = [DiceRoller.roll_d6(explode=True) for _ in range(100)]
    # At least some should be > 6 (exploded)
    assert any(r > 6 for r in results)

def test_roll_dice_count():
    result = DiceRoller.roll_dice(5, False, -1)
    assert len(result.rolls) == 5
    assert all(1 <= r <= 6 for r in result.rolls)

def test_roll_dice_with_tn():
    result = DiceRoller.roll_dice(10, False, 4)
    # Successes should be count of rolls >= 4
    expected = sum(1 for r in result.rolls if r >= 4)
    assert result.successes == expected

def test_opposed_roll():
    att, def_, net = DiceRoller.opposed_roll(
        5, 4, True, 5, 4, True
    )
    assert net == att.successes - def_.successes
```

### 7.2 Integration Tests

**Example: `tests/test_database.py`**

```python
import pytest
import pytest_asyncio
from src.database.db import Database
from bson import ObjectId

@pytest_asyncio.fixture
async def db():
    database = await Database.connect("mongodb://localhost:27017/test_sr1ebot")
    yield database
    await Database.close()

@pytest.mark.asyncio
async def test_folder_creation(db):
    # Create folder
    result = await db.folders.insert_one({
        "name": "test_folder",
        "encrypted": False
    })
    
    assert result.inserted_id is not None
    
    # Clean up
    await db.folders.delete_one({"_id": result.inserted_id})
```

---

## 8. Deployment

### 8.1 Requirements File

**`requirements.txt`:**
```
discord.py>=2.3.0
motor>=3.3.0
python-dotenv>=1.0.0
cryptography>=41.0.0
pytest>=7.4.0
pytest-asyncio>=0.21.0
```

### 8.2 Environment Variables

**`.env.example`:**
```
DISCORD_TOKEN=your_discord_token_here
MONGODB_URL=mongodb://username:password@localhost:27017/sr1egamebot
CRYPTO_KEY=your_64_char_hex_key
CRYPTO_IV=your_32_char_hex_iv
LOG_LEVEL=INFO
```

### 8.3 Docker Support

**`Dockerfile`:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY .env .

CMD ["python", "-m", "src.main"]
```

---

## 9. Migration Checklist

- [ ] Set up Python 3.10+ environment
- [ ] Install dependencies from requirements.txt
- [ ] Create database connection layer
- [ ] Implement encryption utilities
- [ ] Implement dice rolling system
- [ ] Implement cache system
- [ ] Create dice commands
- [ ] Create initiative commands
- [ ] Create macro commands
- [ ] Create scene commands
- [ ] Create GM screen commands
- [ ] Create reminder system
- [ ] Create ammo tracking
- [ ] Create admin commands
- [ ] Implement logging
- [ ] Write unit tests
- [ ] Write integration tests
- [ ] Set up CI/CD
- [ ] Create Docker configuration
- [ ] Test MongoDB migration
- [ ] Perform end-to-end testing
- [ ] Deploy to production

---

## 10. Performance Considerations

### 10.1 Async Best Practices
- Always use `await` for I/O operations
- Use `asyncio.gather()` for parallel operations
- Avoid blocking calls in async functions
- Use connection pooling for database

### 10.2 Caching Strategy
- Cache frequently accessed data
- Implement TTL for cache entries
- Clear cache on data updates
- Monitor cache hit rates

### 10.3 Database Optimization
- Create indexes on frequently queried fields
- Use projection to limit returned fields
- Batch operations when possible
- Monitor query performance

---

## 11. Common Pitfalls & Solutions

### 11.1 Async/Await Issues
**Problem:** Mixing sync and async code
**Solution:** Use `asyncio.to_thread()` for sync operations in async context

### 11.2 Database Connections
**Problem:** Connection pool exhaustion
**Solution:** Use Motor's built-in connection pooling, set appropriate pool size

### 11.3 Type Hints
**Problem:** Complex nested types
**Solution:** Use `TypeAlias` and `Protocol` from typing module

### 11.4 Discord.py Differences
**Problem:** Different event names from discord.js
**Solution:** Refer to discord.py documentation for event mapping

---

## 12. Resources

- **Python Documentation:** https://docs.python.org/3/
- **discord.py Documentation:** https://discordpy.readthedocs.io/
- **Motor Documentation:** https://motor.readthedocs.io/
- **Cryptography Documentation:** https://cryptography.io/
- **pytest Documentation:** https://docs.pytest.org/

---

**End of Migration Guide**
