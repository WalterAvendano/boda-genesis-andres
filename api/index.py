import sys
from pathlib import Path

# Añadir directorio raíz al path para importar app
sys.path.append(str(Path(__file__).parent.parent))

from app import app
