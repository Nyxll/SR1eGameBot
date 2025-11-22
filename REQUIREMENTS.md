# SR1eGameBot - Software Requirements Specification

## Document Information
- **Project**: SR1eGameBot
- **Version**: 0.3
- **Author**: Nathan Hawks (AstroMacGuffin#1486)
- **Repository**: https://github.com/NathanHawks/SR1eGameBot
- **License**: UnLicense (Public Domain)
- **Date**: Reverse Engineered November 2025

---

## 1. Executive Summary

SR1eGameBot is a Discord bot designed for tabletop role-playing games, specifically Shadowrun 1st, 2nd, and 3rd editions, with additional support for Cyberpunk 2020 and Cyberpunk RED. The bot provides comprehensive dice rolling mechanics, initiative tracking, game session management, and GM support tools.

---

## 2. System Architecture

### 2.1 Technology Stack
- **Runtime**: Node.js
- **Primary Language**: JavaScript
- **Database**: MongoDB (Community Edition)
- **Discord API**: Discord.js v14.3.0
- **Additional Libraries**:
  - winston v3.7.2 (logging)
  - node-stream-zip v1.15.0 (data migration)
  - ssl-root-cas v1.3.1 (SSL support)
  - ws v7.4.6 (WebSocket)

### 2.2 Deployment Options
- **Self-hosted**: Local machine or private server
- **Cloud**: Heroku with GitHub integration
- **Worker Type**: Requires worker dyno (not web dyno)

### 2.3 System Components

#### Core Files
- `main.js` - Main application entry point, command routing
- `init.js` - System initialization and startup routines
- `api.js` - Core business logic and data access layer
- `db.js` - MongoDB database connection and abstraction
- `config.js` - Configuration management
- `log.js` - Logging system

#### Feature Modules
- `ft_dicebot.js` - Dice rolling mechanics
- `ft_initiative.js` - Initiative system for multiple game systems
- `ft_macro.js` - Saved dice command macros
- `ft_scene.js` - Prepared scene management
- `ft_gmscreen.js` - Virtual GM screen functionality
- `ft_reminders.js` - Session reminder system
- `ft_ammo.js` - Ammunition tracking
- `ft_help.js` - Help command system
- `ft_misc.js` - Miscellaneous utilities

#### Utility Files
- `admin.js` - Administrative commands
- `migrate.js` - Data migration from Google Drive to MongoDB
- `encrypt-db.js` - Database encryption utilities
- `fix-duplicates.js` - Database maintenance
- `make-crypto-vars.js` - Cryptographic key generation
- `get-labels.js` - Discord label fetching

---

## 3. Functional Requirements

### 3.1 Dice Rolling System

#### 3.1.1 Basic Dice Rolling
- **FR-DICE-001**: System shall support rolling XdY dice without modifiers
  - Format: `!X` rolls X six-sided dice
  - Example: `!5` rolls 5d6 without Rule of 6

- **FR-DICE-002**: System shall support totaling dice rolls
  - Format: `!Xt` rolls X dice and totals them
  - Example: `!6t` rolls 6d6 and adds them together

- **FR-DICE-003**: System shall support dice totals with modifiers
  - Format: `!Xt +/-Z` rolls X dice, totals, and applies modifier
  - Example: `!6t -5` rolls 6d6, totals, and subtracts 5

#### 3.1.2 Shadowrun-Specific Mechanics
- **FR-DICE-004**: System shall implement Rule of 6 (exploding dice)
  - When a 6 is rolled, it counts and triggers an additional roll
  - Format: `!X!` for Rule of 6
  - Recursive: Additional 6s continue to explode

- **FR-DICE-005**: System shall support Target Number (TN) rolls
  - Count successes where roll >= TN
  - Format: `!X tnY` or `!X! tnY`
  - Example: `!5! tn4` rolls 5d6 with Rule of 6 vs TN4

#### 3.1.3 Opposed Rolls
- **FR-DICE-006**: System shall support opposed success tests
  - Format: `!A! tnB vsX! otnY`
  - Compares net successes between attacker and defender
  - Both sides may use Rule of 6
  - Example: `!5! tn3 vs6! otn4`

#### 3.1.4 Advanced Features
- **FR-DICE-007**: System shall support multiple rolls per command
  - Semicolon-separated roll commands
  - Example: `!1 ; 2t ; 3!; 4t +5`

- **FR-DICE-008**: System shall support roll annotations
  - Free-form text notes with rolls
  - Notes can appear anywhere except at the start
  - Example: `!3! TN4 resist wagemage sorcery`

- **FR-DICE-009**: System shall provide re-roll functionality
  - Users can click 🎲 reaction to re-roll
  - Works on recent rolls only
  - Any user can trigger re-roll

- **FR-DICE-010**: System shall sort dice results in descending order
  - Improves readability of results
  - Applied to all roll outputs

### 3.2 Macro System

- **FR-MACRO-001**: System shall allow saving named dice commands
  - Format: `!save macroName diceCommand`
  - Stores per user per channel
  - Example: `!save attack 8! tn5`

- **FR-MACRO-002**: System shall allow rolling saved macros
  - Format: `!roll macroName`
  - Executes stored dice command

- **FR-MACRO-003**: System shall allow listing saved macros
  - Format: `!lm` or `!listmacros`
  - Shows all macros for current user in current channel

- **FR-MACRO-004**: System shall allow deleting macros
  - Format: `!removemacro name` or `!rmm name`
  - Removes specified macro

### 3.3 Initiative System

#### 3.3.1 Player Setup
- **FR-INIT-001**: Players must designate a GM
  - Format: `!setgm @someone`
  - Links player to GM for initiative tracking

- **FR-INIT-002**: Players must set their initiative formula
  - Format: `!setinit X Y` where X=dice, Y=modifier
  - Example: `!setinit 1 4` = 1d6+4
  - Auto-converts to d10 for Cyberpunk systems

#### 3.3.2 GM Setup
- **FR-INIT-003**: GM must designate themselves
  - Format: `!setgm` (no arguments)

- **FR-INIT-004**: GM must set player list
  - Format: `!setplayers @player1 @player2 ...`
  - Requires proper Discord @mentions (blue highlight)

- **FR-INIT-005**: GM can add players to existing list
  - Format: `!addplayers @player1 @player2 ...`

- **FR-INIT-006**: GM can remove players from list
  - Format: `!removeplayers @player1 @player2 ...`

- **FR-INIT-007**: GM can clear entire player list
  - Format: `!clearplayers`

- **FR-INIT-008**: GM can list current players
  - Format: `!listplayers` or `!lp`

#### 3.3.3 NPC Management
- **FR-INIT-009**: System shall support NPC initiative formulas
  - Format: `!setnpcinits X Y label [X2 Y2 label2 ...]`
  - Labels cannot contain spaces or commas
  - Example: `!addnpcinits 1 5 thugs`

- **FR-INIT-010**: System shall allow adding NPCs to existing list
  - Format: `!addnpcinits X Y label ...`

- **FR-INIT-011**: System shall allow listing NPCs
  - Format: `!listnpcinits` or `!ln`

- **FR-INIT-012**: System shall allow removing NPCs
  - Format: `!removenpcinits label1 label2 ...`

- **FR-INIT-013**: System shall allow clearing all NPCs
  - Format: `!clearnpcinits` or `!clrn`

#### 3.3.4 Initiative Rolling
- **FR-INIT-014**: System shall support Shadowrun 1e initiative
  - Format: `!init`
  - Standard forward-counting initiative

- **FR-INIT-015**: System shall support Shadowrun 1e reverse initiative
  - Format: `!initflip`
  - Countdown initiative style

- **FR-INIT-016**: System shall support Shadowrun 2e initiative
  - Format: `!init2` and `!init2flip`

- **FR-INIT-017**: System shall support Shadowrun 3e initiative
  - Format: `!init3` and `!init3flip`

- **FR-INIT-018**: System shall support Cyberpunk 2020 initiative
  - Format: `!initcp`
  - Uses d10 instead of d6

- **FR-INIT-019**: System shall support Cyberpunk RED initiative
  - Format: `!initcpr`

- **FR-INIT-020**: System shall handle initiative passes correctly
  - Displays multiple passes for characters
  - Sorts by initiative value within passes
  - Handles tiebreakers appropriately

#### 3.3.5 Context Management
- **FR-INIT-021**: Initiative data shall be scoped to GM and channel
  - Different channels are independent
  - Multiple GMs can share a channel
  - Players in multiple games must setup separately

### 3.4 Scene Management

- **FR-SCENE-001**: System shall allow creating named scenes
  - Format: `!setscene name [musicLink] sceneText`
  - Music link is optional (YouTube, etc.)
  - Scene text supports Discord formatting and line breaks
  - Limited by Discord message length (2000 characters)

- **FR-SCENE-002**: System shall allow deploying scenes
  - Format: `!getscene name`
  - Scene name is not displayed in output
  - Music shown as link with embedded player

- **FR-SCENE-003**: System shall allow listing scenes
  - Format: `!listscenes`
  - Shows scene names in current channel

- **FR-SCENE-004**: System shall allow deleting scenes
  - Format: `!delscene name1 name2 ...`
  - Multiple scenes can be deleted at once
  - Deletion is permanent (no recovery)

### 3.5 Virtual GM Screen

- **FR-GMSCREEN-001**: System shall support hidden GM channel
  - Allows GM to prep in secret
  - Separate from player-visible channel

- **FR-GMSCREEN-002**: GM shall link hidden channel to play channel
  - Format: `!setchannel #playChannel`
  - Channel link must be properly formatted (blue highlight)

- **FR-GMSCREEN-003**: System shall check current play channel
  - Format: `!checkchannel`

- **FR-GMSCREEN-004**: Scene deployment shall respect GM screen
  - `!getscene` outputs to play channel from hidden channel
  - Scene titles remain hidden

- **FR-GMSCREEN-005**: Initiative commands shall respect GM screen
  - Can prep NPCs in secret
  - Can roll init in either channel

### 3.6 Reminder System

- **FR-REMIND-001**: System shall schedule game session reminders
  - Format: `!addreminder YYYY-MM-DDTHH:MM timer1 timer2 ...`
  - Time is in GMT+0 timezone
  - Hour in 24-hour format
  - Timers: minutes (m), hours (h), days (d)
  - Example: `!addreminder 2022-05-04T18:00 30m 6h 1d 3d 7d`

- **FR-REMIND-002**: System shall send DM reminders
  - Reminders sent to all players in player list
  - Players determined at time of reminder creation
  - Sent via Discord Direct Message

- **FR-REMIND-003**: System shall list upcoming reminders
  - Format: `!listreminders`
  - Shows reminder IDs for cancellation
  - Shows who will receive each reminder
  - May be slow with many reminders

- **FR-REMIND-004**: System shall allow canceling reminders
  - Format: `!cancelreminder id1 id2 ...`
  - Uses IDs from `!listreminders`

- **FR-REMIND-005**: Reminders shall persist across bot restarts
  - Stored in MongoDB
  - Reactivated on startup

### 3.7 Ammo Tracking

#### 3.7.1 Weapon Management
- **FR-AMMO-001**: System shall track weapon definitions
  - Format: `!ammo addgun name maxROF containerType capacity ammoTypes`
  - Name must not have spaces or commas
  - Example: `!ammo addgun uzi3 7 clip 16 slug`

- **FR-AMMO-002**: System shall allow removing weapons
  - Format: `!ammo delgun name`

#### 3.7.2 Ammunition Management
- **FR-AMMO-003**: System shall track ammunition inventory
  - Format: `!ammo addammo qtyContainers containerType qtyRounds roundType maxRounds`
  - Example: `!ammo addammo 10 clip 16 slug 16`

- **FR-AMMO-004**: System shall allow removing ammunition
  - Format: `!ammo delammo qtyContainers containerType qtyRounds roundType maxRounds`

#### 3.7.3 Combat Operations
- **FR-AMMO-005**: System shall track ammunition expenditure
  - Format: `!ammo fire weaponName shots`
  - Enforces maximum ROF
  - Reports when weapon runs dry

- **FR-AMMO-006**: System shall support weapon reloading
  - Format: `!ammo reload weaponName [shotType]`
  - Shot type optional if only one compatible ammo
  - Requires matching ammunition in inventory

- **FR-AMMO-007**: System shall list current inventory
  - Format: `!ammo list`
  - Shows weapons and loaded ammunition
  - Shows available ammunition
  - Empty magazines not shown

### 3.8 Help System

- **FR-HELP-001**: System shall provide comprehensive help
  - Format: `!help` or `!inithelp`
  - Context-sensitive help topics

- **FR-HELP-002**: Help shall cover all features
  - Dice rolling
  - Initiative system
  - Scenes
  - GM Screen
  - Reminders
  - Ammo tracking

### 3.9 Administrative Features

- **FR-ADMIN-001**: System shall support admin-only commands
  - Hardcoded to bot author's Discord ID
  - Self-hosters can change via find/replace

- **FR-ADMIN-002**: Admin can open files for inspection
  - Format: `!open` (admin only)

- **FR-ADMIN-003**: Admin can view cache
  - Format: `!showcache` (admin only)

- **FR-ADMIN-004**: Admin can clear cache
  - Format: `!clearcache` (admin only)

### 3.10 User Preferences

- **FR-PREF-001**: Users can skip maintenance status messages
  - Format: `!skipstatus`
  - Hides recurring system messages

- **FR-PREF-002**: Users can generate web link codes
  - Format: `!link`
  - For web integration features

---

## 4. Non-Functional Requirements

### 4.1 Performance

- **NFR-PERF-001**: Commands shall respond within 2 seconds under normal load
- **NFR-PERF-002**: System shall handle multiple concurrent users across servers
- **NFR-PERF-003**: Cache system shall optimize repeated database queries
- **NFR-PERF-004**: Database queries shall use encryption/decryption efficiently

### 4.2 Security

- **NFR-SEC-001**: Discord authentication token must be stored securely
  - Never committed to version control
  - Stored in `discordauth.json` or environment variable
  - File must be in `.gitignore`

- **NFR-SEC-002**: MongoDB credentials must be protected
  - Stored in `config.js` (not committed to git)
  - Connection string includes authentication
  - Password encoding supported for special characters

- **NFR-SEC-003**: User data shall be encrypted at rest
  - AES-256-CBC encryption for sensitive data
  - Cryptographic keys stored in config
  - Server/channel/user folder names encrypted
  - File contents encrypted

- **NFR-SEC-004**: MongoDB should be secured
  - Password authentication enabled
  - Hosted on same server as bot (recommended)
  - Firewall blocks external connections
  - Only accepts localhost connections

- **NFR-SEC-005**: Admin commands restricted to authorized users
  - Discord ID-based authorization
  - Hardcoded in source code
  - Self-hosters can modify via find/replace

### 4.3 Reliability

- **NFR-REL-001**: System shall handle network disconnections gracefully
  - Automatic reconnection to Discord
  - Error logging for troubleshooting
  - Resume operation after temporary outages

- **NFR-REL-002**: System shall persist data across restarts
  - All user data in MongoDB
  - Reminders restored on startup
  - No data loss from bot restart

- **NFR-REL-003**: System shall handle Discord API errors
  - Graceful error handling for all Discord operations
  - User-friendly error messages
  - Logging for debugging

### 4.4 Scalability

- **NFR-SCALE-001**: System shall support multiple Discord servers
  - Independent data per server
  - No cross-server data leakage
  - Concurrent operation across servers

- **NFR-SCALE-002**: System shall support multiple channels per server
  - Independent game sessions per channel
  - Data scoped to server/channel/user hierarchy

- **NFR-SCALE-003**: System shall support multiple GMs per server
  - GMs can operate in same or different channels
  - Player can participate in multiple games

### 4.5 Usability

- **NFR-USE-001**: Commands shall be case-insensitive
  - User convenience
  - Reduces input errors

- **NFR-USE-002**: Commands shall use intuitive syntax
  - Follows tabletop gaming conventions
  - Short aliases for common commands
  - Natural language options

- **NFR-USE-003**: System shall provide helpful error messages
  - Clear explanation of what went wrong
  - Guidance on correct usage
  - Link to bug reporting when needed

- **NFR-USE-004**: Help documentation shall be comprehensive
  - Available via `!help` command
  - Covers all features
  - Examples provided

### 4.6 Maintainability

- **NFR-MAINT-001**: Code shall be modular
  - Feature modules separate from core
  - Clear separation of concerns
  - Reusable utility functions

- **NFR-MAINT-002**: System shall support data migration
  - Migration script for legacy Google Drive data
  - MongoDB database migration support
  - Upgrade path preservation

- **NFR-MAINT-003**: System shall provide logging
  - Winston-based logging framework
  - Multiple log levels (spam, write, error)
  - Timestamped log entries

- **NFR-MAINT-004**: Configuration shall be externalized
  - Separate config file
  - Environment variable support
  - No hardcoded sensitive data

---

## 5. Data Model

### 5.1 Database Structure

The system uses MongoDB with the following collections:

#### 5.1.1 folders Collection
Hierarchical folder structure for organizing user data:
- **UserData** (root)
  - **serverID** (Discord server ID, encrypted)
    - **channelID** (Discord channel ID, encrypted)
      - **userID** (Discord user ID, encrypted)
        - Contains user-specific files
  - **reminders** (system folder)
    - Contains active reminders
  - **options** (system folder)
    - **userID** folders for user preferences

**Schema**:
```javascript
{
  _id: ObjectId,
  name: String (encrypted or plaintext),
  parent: ObjectId (reference to parent folder),
  label: String (encrypted Discord display name),
  encrypted: Boolean
}
```

#### 5.1.2 strings Collection
Stores file content:

**Schema**:
```javascript
{
  _id: ObjectId,
  name: String (filename),
  parent: ObjectId (reference to parent folder),
  content: String (encrypted or plaintext),
  encrypted: Boolean
}
```

### 5.2 File Types (stored as strings)

#### User Data Files
- **gmFile** - GM designation (stores GM's Discord ID)
- **initFile** - Initiative formula (XdY+Z format)
- **playersFile** - Player list (space-separated Discord IDs)
- **npcFile** - NPC initiative data (comma-separated entries)
- **macros** - Saved dice macros (one per line)
- **gmPlayChannel** - Play channel ID (for GM screen feature)
- **gmReminders** - User's reminders list
- **gmSceneList** - Scene index
- **scene_[name]** - Individual scene content
- **guns** - Weapon inventory
- **ammos** - Ammunition inventory

#### System Files
- **activeReminders** - Global reminders queue

#### User Option Files
- **skipStatusMsg** - Status message preference
- **webLinkCode** - Web integration code

### 5.3 Cache Structure

In-memory cache to optimize database queries:

```javascript
global.cache = {
  server: [],        // {dbID, discordID}
  channel: [],       // {dbID, discordID, parentID}
  userInChannel: [], // {dbID, discordID, parentID}
  file: [],          // {dbID, discordID, parentID}
  fileContent: [],   // {dbID, content}
  playChannel: [],   // {server, channel, user, playChannel}
  triplet: []        // {server, channel, user, dbID}
}
```

---

## 6. External Interfaces

### 6.1 Discord API

- **Discord.js v14.3.0**
- **Required Intents**:
  - Guilds
  - GuildMessages
  - GuildMessageReactions
  - DirectMessages
  - MessageContent
- **Required Partials**:
  - Channel (for DMs)

### 6.2 MongoDB API

- **MongoDB Node.js Driver v4.9.1**
- **Database**: sr1egamebot
- **Connection**: Standard MongoDB connection string
- **Authentication**: SCRAM client authentication

### 6.3 User Interface

All interaction via Discord text commands:
- **Command Prefix**: `!`
- **Response**: Bot replies in same channel
- **DMs**: Used for reminders
- **Reactions**: For re-roll functionality

---

## 7. Installation & Deployment Requirements

### 7.1 Prerequisites

- **Node.js**: Compatible version for Discord.js v14
- **MongoDB**: Community Edition or compatible
- **Discord Bot Token**: From Discord Developer Portal
- **Network**: Internet connection for Discord API
- **Permissions**: Write access to installation directory

### 7.2 Installation Steps

1. Install Node.js and MongoDB
2. Create Discord application and obtain token
3. Clone/download bot source code
4. Copy `config.example.js` to `config.js`
5. Configure MongoDB connection string in `config.js`
6. Create `discordauth.json` with bot token
7. Generate encryption keys with `make-crypto-vars.js`
8. Add `config.js` and `discordauth.json` to `.gitignore`
9. Install dependencies: `npm install`
10. Start MongoDB service
11. Run bot: `node .` or `node main.js`

### 7.3 MongoDB Setup

- Create database: `sr1egamebot`
- Create initial collection: `folders`
- Enable password authentication (recommended)
- Configure firewall (recommended)
- Test connection with MongoDB Compass

### 7.4 Discord Bot Configuration

**Required Permissions** (permission integer: 3136):
- Send Messages
- Embed Links
- Attach Files
- Read Message History
- Add Reactions
- Use External Emojis

### 7.5 Heroku Deployment

1. Link GitHub repository to Heroku
2. Set environment variable `TOKEN` with Discord auth token
3. Configure auto-deploy from master branch
4. Use worker dyno (not web dyno)
5. Ensure MongoDB connection (MongoDB Atlas recommended)

### 7.6 Data Migration

For users migrating from Google Drive version:
1. Download UserData folder from Google Drive
2. Rename to `UserData.zip`
3. Place in bot directory
4. Run: `node ./migrate.js`
5. Verify migration in MongoDB

---

## 8. Testing Requirements

### 8.1 Functional Testing

- **Dice Rolling**: Verify all dice command formats
- **Initiative**: Test all game systems (SR1e, 2e, 3e, CP2020, CPR)
- **Macros**: Create, roll, list, delete operations
- **Scenes**: Create, deploy, list, delete operations
- **GM Screen**: Channel linking and command routing
- **Reminders**: Scheduling, delivery, cancellation
- **Ammo**: Weapon/ammo management, firing, reloading

### 8.2 Integration Testing

- **Discord API**: Connection, reconnection, error handling
- **MongoDB**: CRUD operations, encryption/decryption
- **Multi-user**: Concurrent operations
- **Multi-server**: Data isolation

### 8.3 Security Testing

- **Authentication**: Token protection
- **Encryption**: Data at rest
- **Authorization**: Admin command restriction
- **Input Validation**: Prevent injection attacks

### 8.4 Performance Testing

- **Response Time**: Command execution speed
- **Concurrent Users**: Multiple simultaneous operations
- **Database Load**: Query optimization via cache
- **Memory Usage**: Cache size management

---

## 9. Maintenance & Support

### 9.1 Logging

- **Winston Framework**: Structured logging
- **Log Levels**:
  - `logSpam`: Verbose debugging
  - `logWrite`: Normal operations
  - `logError`: Errors and exceptions
- **Timestamps**: NY timezone
- **Color Coding**: Terminal output

### 9.2 Monitoring

- **Discord Connection**: Status monitoring
- **Database Connection**: Connection health
- **Reminder System**: Active reminder count
- **Error Tracking**: Exception logging

### 9.3 Backup & Recovery

- **MongoDB Backups**: Regular database dumps
- **Configuration**: Backup config files
- **Encryption Keys**: Secure key storage
- **Disaster Recovery**: Database restoration procedure

### 9.4 Bug Reporting

- **GitHub Issues**: Primary bug tracking
- **In-app Command**: `/reportbug` slash command
- **Error Context**: Timestamp, command, args provided

---

## 10. Known Limitations

### 10.1 Technical Limitations

- **Discord Message Length**: 2000 character limit for scenes
- **Reminder Precision**: Based on setTimeout accuracy
- **Cache Persistence**: In-memory cache lost on restart
- **Concurrent Modifications**: No optimistic locking

### 10.2 Feature Limitations

- **Multi-channel Games**: Require separate setup per channel
- **Macro Sharing**: Macros not shared between users
- **Scene Versioning**: No scene history/rollback
- **Ammo Containers**: Empty magazines not tracked

### 10.3 Platform Limitations

- **Discord Rate Limits**: API call restrictions apply
- **MongoDB Size**: Storage limits based on hosting
- **Node.js Memory**: Heap size limitations
- **Network Dependency**: Requires internet connection

---

## 11. Future Enhancement Possibilities

### 11.1 Potential Features

- Character sheet storage
- Dice pool management
- Combat tracking
- Skill roll templates
- Campaign notes
- Session logging
- Player statistics
- Custom dice types
- Slash commands support
- Web interface for GM tools

### 11.2 Technical Improvements

- Microservices architecture
- Redis caching layer
- Database sharding
- Load balancing
- GraphQL API
- Real-time websocket updates
- Automated testing suite
- CI/CD pipeline
- Docker containerization
- Kubernetes orchestration

---

## 12. Glossary

- **Rule of 6**: Shadowrun mechanic where rolling a 6 allows additional roll
- **TN (Target Number)**: Minimum value needed for success
- **Initiative Pass**: Additional turns in Shadowrun combat
- **GM Screen**: Private channel for GM preparation
- **Macro**: Saved dice command template
- **Scene**: Prepared narrative text with optional music
- **ROF (Rate of Fire)**: Maximum shots per action
- **Triplet**: Server/Channel/User hierarchy in database
- **Discord ID**: Unique numerical identifier (Snowflake)
- **MongoDB ObjectId**: 12-byte unique identifier

---

## 13. References

- Discord.js Documentation: https://discord.js.org/
- MongoDB Documentation: https://docs.mongodb.com/
- Shadowrun Rules (1e/2e/3e)
- Cyberpunk 2020 Rules
- Cyberpunk RED Rules
- GitHub Repository: https://github.com/NathanHawks/SR1eGameBot

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | Nov 2025 | Reverse Engineering | Initial requirements document created from source code analysis |

---

**End of Requirements Specification**
