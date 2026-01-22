# A tool to parser CAN data from Aceinna IMU devices and visualize it.

## 1. Environment Setup

To ensure a clean environment and faster packaging, it is recommended to use a fresh virtual environment.

```bash
# Create venv
python -m venv venv

# Activate venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## 2. Development environment run
```
python main.py
```

## 3. Packaging with PyInstaller

Run PyInstaller with the spec file:

```bash
pyinstaller --clean --noconfirm build.spec
```

The `--clean` flag helps clear PyInstaller caches.

