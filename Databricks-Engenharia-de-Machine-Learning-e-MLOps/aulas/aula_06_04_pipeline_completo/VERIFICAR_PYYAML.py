import importlib.util

modulo = importlib.util.find_spec("yaml")

if modulo is None:
    print("PyYAML: AUSENTE")
    raise SystemExit(3)

print("PyYAML: INSTALADO")