# Steam Shelf

Add and organize legally-owned non-Steam games in your Steam library, complete with custom artwork and metadata. Keep your collection fully integrated into Steam.

## 🚀 Quick Start

### GUI Version (Recommended)

```bash
python scripts/steam-shelf-gui.py
```

### CLI Version

```bash
python scripts/steam-shelf.py /path/to/games/directory
```

## 📁 Project Structure

The project has been restructured for better maintainability and development:

```
steam-shelf/
├── src/                          # 🏗️ Main source code
│   ├── core/                     # 🧠 Core business logic (UI-independent)
│   │   ├── models/              # 📊 Data models
│   │   │   ├── non_steam_game.py       # Game data structure
│   │   │   └── repository.py           # Game repository management
│   │   ├── services/            # ⚙️ Business services
│   │   │   ├── game_discovery.py       # Game discovery logic
│   │   │   ├── game_validator.py       # Game validation
│   │   │   ├── image_client.py         # Steam image handling
│   │   │   └── steam_db_utils.py       # Steam database utilities
│   │   └── utils/               # 🔧 Utility modules
│   │       ├── shortcut_utils.py       # Steam shortcut utilities
│   │       ├── vdf_serializer.py       # VDF serialization
│   │       └── vdf_utils.py            # VDF parsing utilities
│   ├── cli/                     # 💻 Command-line interface
│   │   └── commands.py          # CLI commands and logic
│   └── gui/                     # 🖼️ Graphical user interface
│       ├── main_window.py       # Main GUI application
│       ├── widgets/             # GUI components
│       └── utils/               # GUI-specific utilities
├── scripts/                     # 🚀 Entry points
│   ├── steam-shelf.py          # CLI entry point
│   ├── steam-shelf-gui.py      # GUI entry point
│   └── steam-shelf.bat         # Windows batch file
├── tests/                       # 🧪 Test files
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   └── fixtures/              # Test data
├── docs/                       # 📚 Documentation
├── config/                     # ⚙️ Configuration files
├── requirements.txt            # 📦 Dependencies
└── LICENSE
```

## 🏗️ Architecture Benefits

### ✅ **Better Organization**

- **Separation of Concerns**: Core logic is independent of UI
- **Modular Design**: Easy to add new features or interfaces
- **Clear Dependencies**: Reduced coupling between components

### ✅ **Improved Development**

- **Scalable**: Add new features without cluttering
- **Testable**: Well-organized test structure
- **Maintainable**: Clear boundaries between different concerns
- **Professional**: Follows Python packaging best practices

### ✅ **Reusability**

- Core logic can be imported by both CLI and GUI
- Easy to create new interfaces (web, API, etc.)
- Clean separation allows for better testing

## 🔧 Development

### Installation

```bash
pip install -r requirements.txt
```

### Running Tests

```bash
# Run all tests
pytest

# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/integration/
```

### Development Guidelines

- Core business logic goes in `src/core/`
- UI-specific code goes in `src/cli/` or `src/gui/`
- All tests should be in `tests/` with appropriate subdirectories
- Use relative imports within the src package

## 📋 Legacy Files

The following files remain in the root for compatibility but will be removed in future versions:

- `main.py` → Use `scripts/steam-shelf.py`
- `gui.py` → Use `scripts/steam-shelf-gui.py`
- `cli.py` → Moved to `src/cli/commands.py`
