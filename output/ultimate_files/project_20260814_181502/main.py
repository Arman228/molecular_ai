import json
import csv
import asyncio
import hashlib
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
import redis
import websockets
from pathlib import Path

# === JSONParser для конфигурации ===
class JSONParser:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return self.create_default_config()
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON config: {e}")
    
    def create_default_config(self) -> Dict[str, Any]:
        default_config = {
            "redis": {"host": "localhost", "port": 6379, "db": 0},
            "websocket": {"host": "localhost", "port": 8765},
            "rate_limit": {"max_requests": 100, "window_seconds": 60},
            "files": {"input_dir": "./data/input", "output_dir": "./data/output"}
        }
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=4)
        return default_config
    
    def get(self, key: str, default: Any = None) -> Any:
        return self.config.get(key, default)

# === FileProcessor для работы с файлами ===
class FileProcessor:
    def __init__(self, input_dir: str, output_dir: str):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.ensure_directories()
    
    def ensure_directories(self):
        self.input_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def read_file(self, filename: str) -> str:
        file_path = self.input_dir / filename
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def write_file(self, filename: str, content: str):
        file_path = self.output_dir / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def list_files(self) -> List[str]:
        return [f.name for f in self.input_dir.iterdir() if f.is_file()]
    
    def delete_file(self, filename: str):
        file_path = self.input_dir / filename
        if file_path.exists():
            file_path.unlink()

# === CSVProcessor для отчетов ===
class CSVProcessor:
    def __init__(self, file_processor: FileProcessor):
        self.file_processor = file_processor
    
    def generate_report(self, data: List[Dict[str, Any]], filename: str):
        if not data:
            return
        
        headers = list(data[0].keys())
        file_path = self.file_processor.output_dir / filename
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(data)
    
    def read_report(self, filename: str) -> List[Dict[str, Any]]:
        file_path = self.file_processor.input_dir / filename
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)
    
    def append_to_report(self, data: Dict[str, Any], filename: str):
        file_path = self.file_processor.output_dir / filename
        headers = list(data.keys())
        
        file_exists = file_path.exists()
        with open(file_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            if not file_exists:
                writer.writeheader()
            writer.writerow(data)

# === RedisCache для кэширования ===
class RedisCache:
    def __init__(self, host: str, port: int, db: int = 0):
        self.client = redis.Redis(host=host, port=port, db=db, decode_responses=True)
    
    def set(self, key: str, value: Any, expiry: int = 300):
        self.client.set(key, json.dumps(value), ex=expiry)
    
    def get(self, key: str) -> Optional[Any]:
        value = self.client.get(key)
        if value:
            return json.loads(value)
        return None
    
    def delete(self, key: str):
        self.client.delete(key)
    
    def exists(self, key: str) -> bool:
        return self.client.exists(key) > 0
    
    def clear_all(self):
        self.client.flushdb()

# === RateLimiter для безопасности ===
class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, List[float]] = {}
    
    def _cleanup(self, key: str, current_time: float):
        if key in self.requests:
            self.requests[key] = [
                timestamp for timestamp in self.requests[key]
                if current_time - timestamp < self.window_seconds
            ]
    
    def is_allowed(self, key: str) -> bool:
        current_time = time.time()
        self._cleanup(key, current_time)
        
        if key not in self.requests:
            self.requests[key] = []
        
        if len(self.requests[key]) >= self.max_requests:
            return False
        
        self.requests[key].append(current_time)
        return True
    
    def get_remaining(self, key: str) -> int:
        current_time = time.time()
        self._cleanup(key, current_time)
        return max(0, self.max_requests - len(self.requests.get(key, [])))

# === WebSocket для чата ===
class ChatWebSocket:
    def __init__(self, host: str, port: int, rate_limiter: RateLimiter):
        self.host = host
        self.port = port
        self.rate_limiter = rate_limiter
        self.clients = set()
        self.chat_history = []
    
    async def handler(self, websocket, path):
        client_id = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        self.clients.add(websocket)
        
        try:
            # Отправляем историю чата
            for msg in self.chat_history[-50:]:
                await websocket.send(json.dumps(msg))
            
            async for message in websocket:
                if not self.rate_limiter.is_allowed(client_id):
                    await websocket.send(json.dumps({"error": "Rate limit exceeded"}))
                    continue
                
                data = json.loads(message)
                chat_message = {
                    "user": data.get("user", "anonymous"),
                    "message": data.get("message", ""),
                    "timestamp": datetime.now().isoformat()
                }
                
                self.chat_history.append(chat_message)
                
                # Рассылаем всем клиентам
                for client in self.clients:
                    try:
                        await client.send(json.dumps(chat_message))
                    except:
                        self.clients.discard(client)
        
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.clients.discard(websocket)
    
    async def start(self):
        async with websockets.serve(self.handler, self.host, self.port):
            print(f"WebSocket chat server started on ws://{self.host}:{self.port}")
            await asyncio.Future()

# === ReactComponent для интерфейса ===
class ReactComponent:
    def __init__(self, file_processor: FileProcessor):
        self.file_processor = file_processor
    
    def generate_html(self, title: str = "Chat Application") -> str:
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; }}
                #chat-container {{ max-width: 800px; margin: 0 auto; }}
                #messages {{ border: 1px solid #ccc; height: 300px; overflow-y: auto; padding: 10px; margin-bottom: 10px; }}
                .message {{ margin-bottom: 10px; padding: 5px; background: #f0f0f0; border-radius: 5px; }}
                .user {{ font-weight: bold; color: #0066cc; }}
                .timestamp {{ font-size: 0.8em; color: #666; }}
                #input-container {{ display: flex; gap: 10px; }}
                input, button {{ padding: 8px; }}
                input {{ flex: 1; }}
                button {{ background: #0066cc; color: white; border: none; cursor: pointer; }}
            </style>
        </head>
        <body>
            <div id="chat-container">
                <h1>{title}</h1>
                <div id="messages"></div>
                <div id="input-container">
                    <input type="text" id="username" placeholder="Username" value="User">
                    <input type="text" id="message-input" placeholder="Type your message...">
                    <button onclick="sendMessage()">Send</button>
                </div>
            </div>
            
            <script>
                const ws = new WebSocket('ws://localhost:8765');
                const messagesContainer = document.getElementById('messages');
                const messageInput = document.getElementById('message-input');
                const usernameInput = document.getElementById('username');
                
                ws.onopen = () => {{
                    console.log('Connected to chat server');
                }};
                
                ws.onmessage = (event) => {{
                    const data = JSON.parse(event.data);
                    if (data.error) {{
                        alert(data.error);
                        return;
                    }}
                    displayMessage(data);
                }};
                
                ws.onerror = (error) => {{
                    console.error('WebSocket error:', error);
                }};
                
                function displayMessage(data) {{
                    const messageElement = document.createElement('div');
                    messageElement.className = 'message';
                    messageElement.innerHTML = `
                        <span class="user">${{data.user}}</span>: 
                        <span>${{data.message}}</span>
                        <div class="timestamp">${{data.timestamp}}</div>
                    `;
                    messagesContainer.appendChild(messageElement);
                    messagesContainer.scrollTop = messagesContainer.scrollHeight;
                }}
                
                function sendMessage() {{
                    const message = messageInput.value.trim();
                    if (!message) return;
                    
                    const data = {{
                        user: usernameInput.value || 'Anonymous',
                        message: message
                    }};
                    
                    ws.send(JSON.stringify(data));
                    messageInput.value = '';
                }}
                
                messageInput.addEventListener('keypress', (e) => {{
                    if (e.key === 'Enter') sendMessage();
                }});
            </script>
        </body>
        </html>
        """
        return html
    
    def render(self, filename: str = "index.html"):
        html_content = self.generate_html()
        self.file_processor.write_file(filename, html_content)
        print(f"React component saved to {self.file_processor.output_dir / filename}")

# === Главный класс приложения ===
class Application:
    def __init__(self, config_path: str = "config.json"):
        self.config_parser = JSONParser(config_path)
        self.config = self.config_parser.config
        
        self.file_processor = FileProcessor(
            input_dir=self.config["files"]["input_dir"],
            output_dir=self.config["files"]["output_dir"]
        )
        
        self.csv_processor = CSVProcessor(self.file_processor)
        
        self.cache = RedisCache(
            host=self.config["redis"]["host"],
            port=self.config["redis"]["port"],
            db=self.config["redis"]["db"]
        )
        
        self.rate_limiter = RateLimiter(
            max_requests=self.config["rate_limit"]["max_requests"],
            window_seconds=self.config["rate_limit"]["window_seconds"]
        )
        
        self.chat_server = ChatWebSocket(
            host=self.config["websocket"]["host"],
            port=self.config["websocket"]["port"],
            rate_limiter=self.rate_limiter
        )
        
        self.react_component = ReactComponent(self.file_processor)
    
    def process_data(self, filename: str) -> Dict[str, Any]:
        # Проверяем кэш
        cache_key = f"processed_data_{filename}"
        cached = self.cache.get(cache_key)
        if cached:
            print(f"Data loaded from cache: {filename}")
            return cached
        
        # Обрабатываем файл
        content = self.file_processor.read_file(filename)
        data = json.loads(content)
        
        # Сохраняем в кэш
        self.cache.set(cache_key, data, expiry=300)
        print(f"Data processed and cached: {filename}")
        return data
    
    def generate_report(self, data: List[Dict[str, Any]], report_name: str):
        self.csv_processor.generate_report(data, report_name)
        print(f"Report generated: {report_name}")
    
    def run_chat_server(self):
        asyncio.run(self.chat_server.start())
    
    def setup_interface(self):
        self.react_component.render()
        print("Web interface generated")
    
    def demo_workflow(self):
        # Демонстрация работы
        print("Starting application demo...")
        
        # Создаем тестовые данные
        sample_data = [
            {"id": 1, "name": "Alice", "message": "Hello World"},
            {"id": 2, "name": "Bob", "message": "Hi Alice"},
            {"id": 3, "name": "Charlie", "message": "Hello everyone"}
        ]
        
        # Сохраняем в файл
        self.file_processor.write_file("sample.json", json.dumps(sample_data))
        print(f"Sample data saved to {self.file_processor.input_dir / 'sample.json'}")
        
        # Обрабатываем и кэшируем
        processed = self.process_data("sample.json")
        print(f"Processed data: {processed}")
        
        # Генерируем отчет
        self.generate_report(sample_data, "chat_report.csv")
        
        # Создаем интерфейс
        self.setup_interface()
        
        print("Demo workflow completed successfully!")

# === Точка входа ===
if __name__ == "__main__":
    app = Application()
    
    # Демонстрация
    app.demo_workflow()
    
    # Запуск WebSocket сервера (раскомментировать для запуска)
    # app.run_chat_server()
