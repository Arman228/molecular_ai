import json, tempfile, os, subprocess, sys

with open('data/skills_registry.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

skills = list(data['registry'].values())
skill = skills[0]  # PatternResonance
code = skill['code']
tests = skill['tests']

# Strip imports
cleaned = '\n'.join(line for line in tests.splitlines() if not line.strip().startswith(('from ', 'import ')))

with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
    f.write(code)
    f.write('\n\n')
    f.write(cleaned)
    tmp = f.name

print('=== CODE (first 500 chars) ===')
print(code[:500])
print('\n=== TESTS (first 500 chars) ===')
print(cleaned[:500])

r = subprocess.run([sys.executable, '-m', 'pytest', tmp, '-v'], capture_output=True, text=True, encoding='utf-8')
print('\n=== STDOUT ===')
print(r.stdout)
print('\n=== STDERR ===')
print(r.stderr)
print('\n=== RETURN CODE ===')
print(r.returncode)

os.unlink(tmp)