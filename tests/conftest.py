import os
from pathlib import Path

from dotenv import load_dotenv


TEST_ENV_FILE = Path.home() / ".nuclear_sim_test_env"

if not TEST_ENV_FILE.exists():
    raise RuntimeError(
        f"No se encuentra el entorno de pruebas: {TEST_ENV_FILE}"
    )

load_dotenv(TEST_ENV_FILE, override=True)
