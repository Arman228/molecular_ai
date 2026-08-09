#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dynamic Multi-Agent Code Generation v1.
Пользователь вводит задачу → анализатор определяет модули → 
создаётся N агентов → каждый генерирует свой модуль → сборка.
"""

import os
import sys
import re
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.system import MolecularSystem


# === TASK ANALYZER ===

MODULE_PATTERNS = {
    "backend": ["api", "rest", "flask", "django", "fastapi", "server", "backend", "endpoint"],
    "frontend": ["react", "vue", "angular", "html", "css", "js", "javascript", "frontend", "ui"],
    "auth": ["jwt", "oauth", "auth", "login", "password", "session", "token", "security"],
    "database": ["postgres", "mongodb", "sqlite", "mysql", "db", "database", "orm", "sql"],
    "tests": ["test", "pytest", "unittest", "spec", "coverage"],
    "docs": ["readme", "documentation", "doc", "swagger", "openapi"],
    "config": ["docker", "dockerfile", "ci/cd", "github actions", "deploy", "nginx"],
}


def analyze_task(task: str) -> dict:
    """
    Анализирует задачу и определяет необходимые модули.
    Возвращает {module_name: keywords_found}.
    """
    task_lower = task.lower()
    detected = {}
    
    for module, keywords in MODULE_PATTERNS.items():
        found = [kw for kw in keywords if kw in task_lower]
        if found:
            detected[module] = found
    
    # Если ничего не найдено — минимум 1 агент (generic coder)
    if not detected:
        detected["generic"] = ["code"]
    
    return detected


def estimate_complexity(task: str, modules: dict) -> dict:
    """
    Оценивает сложность каждого модуля (1-10).
    """
    task_lower = task.lower()
    complexity = {}
    
    for module in modules:
        base = 3  # базовая сложность
        
        # +1 за каждое дополнительное ключевое слово
        base += len(modules[module]) * 0.5
        
        # +2 за сложные паттерны
        if any(w in task_lower for w in ["microservice", "distributed", "async", "websocket"]):
            base += 2
        if any(w in task_lower for w in ["machine learning", "ai", "neural", "model"]):
            base += 2
        if any(w in task_lower for w in ["real-time", "streaming", "kafka", "redis"]):
            base += 1.5
            
        complexity[module] = min(int(base), 10)
    
    return complexity


# === MOCK CODE GENERATORS ===

MOCK_CODE = {
    "backend": '''from flask import Flask, jsonify, request
from functools import wraps
import jwt
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'

# In-memory storage (replace with DB in production)
users = {}

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        except:
            return jsonify({'message': 'Token is invalid'}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/api/users', methods=['GET'])
@token_required
def get_users():
    return jsonify(list(users.values()))

@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json()
    user_id = len(users) + 1
    users[user_id] = {'id': user_id, 'name': data.get('name'), 'email': data.get('email')}
    return jsonify(users[user_id]), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    token = jwt.encode(
        {'user': data.get('username'), 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)},
        app.config['SECRET_KEY'],
        algorithm="HS256"
    )
    return jsonify({'token': token})

if __name__ == '__main__':
    app.run(debug=True)''',

    "frontend": '''import React, { useState, useEffect } from 'react';

function App() {
  const [users, setUsers] = useState([]);
  const [token, setToken] = useState(localStorage.getItem('token') || '');

  useEffect(() => {
    if (token) {
      fetch('/api/users', { headers: { 'Authorization': token } })
        .then(r => r.json())
        .then(data => setUsers(data));
    }
  }, [token]);

  const login = async (username, password) => {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    const data = await res.json();
    setToken(data.token);
    localStorage.setItem('token', data.token);
  };

  return (
    <div>
      <h1>User Management</h1>
      {!token && <LoginForm onLogin={login} />}
      {token && <UserList users={users} />}
    </div>
  );
}

function LoginForm({ onLogin }) {
  const [user, setUser] = useState('');
  const [pass, setPass] = useState('');
  return (
    <form onSubmit={e => { e.preventDefault(); onLogin(user, pass); }}>
      <input value={user} onChange={e => setUser(e.target.value)} placeholder="Username" />
      <input type="password" value={pass} onChange={e => setPass(e.target.value)} placeholder="Password" />
      <button type="submit">Login</button>
    </form>
  );
}

function UserList({ users }) {
  return (
    <ul>
      {users.map(u => <li key={u.id}>{u.name} ({u.email})</li>)}
    </ul>
  );
}

export default App;''',

    "auth": '''import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify

class AuthManager:
    def __init__(self, secret_key):
        self.secret_key = secret_key
        self.blacklist = set()
    
    def generate_token(self, user_id, expires_hours=24):
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(hours=expires_hours),
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def verify_token(self, token):
        if token in self.blacklist:
            return None
        try:
            return jwt.decode(token, self.secret_key, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def revoke_token(self, token):
        self.blacklist.add(token)
    
    def token_required(self, f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
            if not token:
                return jsonify({'message': 'Token is missing'}), 401
            data = self.verify_token(token)
            if not data:
                return jsonify({'message': 'Token is invalid'}), 401
            return f(*args, **kwargs)
        return decorated''',

    "database": '''from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    created_at = Column(Integer)

class DatabaseManager:
    def __init__(self, db_url='sqlite:///app.db'):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
    
    def create_user(self, username, email, password_hash):
        session = self.Session()
        user = User(username=username, email=email, password_hash=password_hash)
        session.add(user)
        session.commit()
        user_id = user.id
        session.close()
        return user_id
    
    def get_user(self, user_id):
        session = self.Session()
        user = session.query(User).filter_by(id=user_id).first()
        result = {'id': user.id, 'username': user.username, 'email': user.email} if user else None
        session.close()
        return result
    
    def get_all_users(self):
        session = self.Session()
        users = [{'id': u.id, 'username': u.username, 'email': u.email} for u in session.query(User).all()]
        session.close()
        return users''',

    "tests": '''import pytest
import json
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_login(client):
    res = client.post('/api/auth/login', json={'username': 'test', 'password': 'test'})
    assert res.status_code == 200
    assert 'token' in res.get_json()

def test_get_users_without_auth(client):
    res = client.get('/api/users')
    assert res.status_code == 401

def test_create_user(client):
    res = client.post('/api/users', json={'name': 'Alice', 'email': 'alice@example.com'})
    assert res.status_code == 201
    data = res.get_json()
    assert data['name'] == 'Alice'

def test_get_users_with_auth(client):
    # Login first
    login_res = client.post('/api/auth/login', json={'username': 'test', 'password': 'test'})
    token = login_res.get_json()['token']
    
    res = client.get('/api/users', headers={'Authorization': token})
    assert res.status_code == 200
    assert isinstance(res.get_json(), list)''',

    "docs": '''# Project API Documentation

## Authentication
All endpoints (except login) require JWT token in `Authorization` header.

### POST /api/auth/login
Login and receive token.
```json
{"username": "user", "password": "pass"}
{"name": "Alice", "email": "alice@example.com"}

pip install -r requirements.txt
python app.py
```''',

    "config": '''FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "app.py"]

# docker build -t myapp .
# docker run -p 5000:5000 myapp''',

    "generic": '''def main():
    """Main function."""
    print("Hello, World!")

if __name__ == '__main__':
    main()''',
}


def generate_module_code(module_name: str, task: str, complexity: int) -> str:
    """Генерирует код модуля (mock или LLM)."""
    if module_name in MOCK_CODE:
        code = MOCK_CODE[module_name]
        # Добавляем header с метаданными
        header = f'''# Module: {module_name}
# Complexity: {complexity}/10
# Generated for task: {task[:60]}...
# Auto-generated by Molecular AI Dynamic Code Generation

'''
        return header + code
    return f"# Module {module_name} placeholder\n"


# === ORBITAL SYNCHRONIZATION ===

def sync_agents(n_agents: int, steps: int = 300) -> float:
    """Синхронизирует N агентов через orbital."""
    mol = MolecularSystem(
        n_agents=n_agents,
        dt=0.05,
        noise=0.01,
        k_sparse=min(4, n_agents - 1) if n_agents > 4 else 2,
        exc_ratio=0.90,
    )
    for layer in mol.orbital.layers:
        layer.coupling *= 2.5
    
    for _ in range(steps):
        mol.step()
    
    return mol.order_parameter()


# === PROJECT ASSEMBLER ===

def assemble_project(modules: dict, task: str, output_dir: str = "output/project"):
    """Собирает все модули в единый проект."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Сохраняем каждый модуль
    for module_name, code in modules.items():
        ext = ".py" if module_name != "frontend" else ".jsx"
        if module_name == "config":
            ext = ".dockerfile"
        elif module_name == "docs":
            ext = ".md"
        
        filename = os.path.join(output_dir, f"{module_name}{ext}")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(code)
        print(f"    Saved: {filename}")
    
    # Создаём README проекта
    readme = f"""# Auto-Generated Project

**Task:** {task}

**Modules:** {', '.join(modules.keys())}

**Generated by:** Molecular AI Dynamic Code Generation v1

## Structure
"""
    for module in modules:
        readme += f"- `{module}` — auto-generated module\n"
    
    readme_path = os.path.join(output_dir, "README.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme)
    print(f"    Saved: {readme_path}")
    
    # Создаём requirements.txt (heuristic)
    reqs = ["flask", "PyJWT", "sqlalchemy"]
    if "frontend" in modules:
        reqs.append("react")
    if "tests" in modules:
        reqs.append("pytest")
    
    req_path = os.path.join(output_dir, "requirements.txt")
    with open(req_path, "w", encoding="utf-8") as f:
        f.write("\n".join(reqs))
    print(f"    Saved: {req_path}")


# === MAIN ===

def main():
    print("=" * 70)
    print("DYNAMIC CODE GENERATION v1")
    print("Auto-scaling agents by task complexity")
    print("=" * 70)
    
    # Пользователь вводит задачу
    if len(sys.argv) > 1:
        task = " ".join(sys.argv[1:])
    else:
        print("\nEnter your task (e.g., 'Flask REST API with JWT auth and React frontend'):")
        task = input("> ").strip()
    
    if not task:
        task = "Flask REST API with JWT authentication and user CRUD"
        print(f"[Default task: {task}]")
    
    print(f"\n{'='*70}")
    print(f"TASK: {task}")
    print(f"{'='*70}")
    
    # 1. Анализ задачи
    print("\n[1/4] Analyzing task...")
    detected = analyze_task(task)
    complexity = estimate_complexity(task, detected)
    
    print(f"    Detected modules: {list(detected.keys())}")
    for mod, comp in complexity.items():
        print(f"    - {mod}: complexity {comp}/10")
    
    n_agents = len(detected)
    print(f"    → {n_agents} agents required")
    
    # 2. Синхронизация
    print(f"\n[2/4] Synchronizing {n_agents} agents...")
    sync_r = sync_agents(n_agents, steps=300)
    print(f"    Sync r = {sync_r:.3f}")
    
    # 3. Генерация кода
    print("\n[3/4] Generating modules...")
    modules = {}
    for i, (module_name, keywords) in enumerate(detected.items()):
        comp = complexity[module_name]
        print(f"    Agent {i} ({module_name}, complexity={comp})...")
        code = generate_module_code(module_name, task, comp)
        modules[module_name] = code
        print(f"    → {len(code)} chars")
    
    # 4. Сборка
    print("\n[4/4] Assembling project...")
    output_dir = os.path.join(os.path.dirname(__file__), "..", "output", "project")
    assemble_project(modules, task, output_dir)
    
    # Итог
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    print(f"Task:        {task}")
    print(f"Agents:      {n_agents}")
    print(f"Sync r:      {sync_r:.3f}")
    print(f"Modules:     {', '.join(modules.keys())}")
    print(f"Output:      {os.path.abspath(output_dir)}")
    print(f"\nNext steps:")
    print(f"  cd {output_dir}")
    print(f"  pip install -r requirements.txt")
    if "tests" in modules:
        print(f"  pytest tests/ -v")


if __name__ == "__main__":
    main()