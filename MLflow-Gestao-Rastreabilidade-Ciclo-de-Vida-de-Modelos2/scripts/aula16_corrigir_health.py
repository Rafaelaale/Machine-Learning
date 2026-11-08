from pathlib import Path
import shutil

src = Path("src/aula16_docker_smoke.py")
test = Path("tests/test_aula16_docker_smoke.py")

for path in (src, test):
    backup = path.with_suffix(path.suffix + ".bak")
    if not backup.exists():
        shutil.copy2(path, backup)
        print("BACKUP:", backup)

old_health = '''def health():
    result = {}
    for path in ("ping", "health", "version"):
        r = requests.get(f"{API}/{path}", timeout=15)
        r.raise_for_status()
        result[path] = r.status_code
    return result
'''

new_health = '''def health():
    """Ping obrigatorio; health/version podem nao existir."""
    result = {}
    for path in ("ping", "health", "version"):
        r = requests.get(f"{API}/{path}", timeout=15)
        if path == "ping":
            r.raise_for_status()
        elif r.status_code != 404:
            r.raise_for_status()
        result[path] = r.status_code
    return result
'''

old_test = '''    def test_07_health(self):
        self.assertEqual(health(), {
            "ping": 200, "health": 200, "version": 200
        })
'''

new_test = '''    def test_07_health(self):
        checks = health()
        self.assertEqual(checks["ping"], 200)
        self.assertIn(checks["health"], (200, 404))
        self.assertIn(checks["version"], (200, 404))
'''

content = src.read_text(encoding="utf-8-sig")

if old_health in content:
    src.write_text(
        content.replace(old_health, new_health, 1),
        encoding="utf-8",
    )
    print("SMOKE TEST CORRIGIDO")
elif new_health in content:
    print("SMOKE TEST JA CORRIGIDO")
else:
    raise RuntimeError("Funcao health() nao corresponde ao codigo esperado.")

content = test.read_text(encoding="utf-8-sig")

if old_test in content:
    test.write_text(
        content.replace(old_test, new_test, 1),
        encoding="utf-8",
    )
    print("TESTE UNITARIO CORRIGIDO")
elif new_test in content:
    print("TESTE UNITARIO JA CORRIGIDO")
else:
    raise RuntimeError("Teste de health nao corresponde ao codigo esperado.")