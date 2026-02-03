# Quick Start Guide - Project Sentinel Phase 1

## ⚠️ Important: Virtual Environment

The project uses a virtual environment (`.venv`). You have two options:

### Option 1: Use the Helper Script (Recommended)

```bash
# Run all tests
run.bat test

# Run examples
run.bat examples

# Quick test (minimal output)
run.bat test-quick
```

### Option 2: Activate Virtual Environment Manually

```powershell
# Activate virtual environment
.venv\Scripts\Activate.ps1

# Now you can use python directly
python -m pytest tests/ -v
python examples/phase1_examples.py

# Deactivate when done
deactivate
```

### Option 3: Use Full Path to Python

```powershell
# Run tests
.venv\Scripts\python.exe -m pytest tests/ -v

# Run examples
.venv\Scripts\python.exe examples/phase1_examples.py
```

## 🚀 Quick Commands

```bash
# Install/reinstall the package
.venv\Scripts\pip.exe install -e .

# Run specific test file
.venv\Scripts\python.exe -m pytest tests/test_signal_synchronizer.py -v

# Import in Python
.venv\Scripts\python.exe -c "from sentinel import SignalSynchronizer; print('Works!')"
```

## ✅ Verification

All tests passing: **32/32** ✅  
Examples working: **4/4** ✅

Ready for Phase 2! 🎉
