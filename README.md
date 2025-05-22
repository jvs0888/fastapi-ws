## Description:

A WebSocket server built with FastAPI that supports real-time notifications and graceful shutdown.

## Installation
Install poetry:

```curl -sSL https://install.python-poetry.org | python3 -```

Clone the repository:

```git clone https://github.com/jvs0888/fastapi-ws.git```

```cd fastapi-ws```

Install python dependencies:

```poetry install```

## Running the Server:

You can also use additional uvicorn flags

```uvicorn main:app```

## Testing
### Pytest:
- Multiple WebSocket connections — the server correctly handles multiple simultaneous clients.
- Graceful Shutdown — the application shuts down only after all clients disconnect or after 30 minutes have passed since the shutdown signal.

Run pytest:

```pytest```

or using poetry:

```poetry run pytest```

### Manual testing

Endpoint: 

**ws://localhost:8000/ws**

Use a WebSocket client (e.g., wscat, browser-based client, or Postman) to connect to */ws* endpoint.

The server sends messages:

When connected:

```{"type": "CONNECT", "message": "connection was established"}```

Ping notification, every 10 seconds:

```{"type": "INFO", "message": "keep-alive"}```

When disconnected:

```{"type": "DISCONNECT", "message": "connection was disconnected"}```

Warning message, before server shutdown:

```{"type": "WARNING", "message": "connection is closing soon"}```

## Graceful Shutdown Logic

Trigger: 

Initiated by *SIGTERM* or *SIGINT* signals (e.g., Ctrl+C or process termination).

Behavior:
- Tracks active WebSocket connections.
- Waits until all clients disconnect or 30 minutes elapse (whichever comes first).
- Logs shutdown progress (e.g., remaining connections, time left).
- Supports multiple Uvicorn workers by ensuring proper connection cleanup.



Implementation:





- Uses a connection manager to track active WebSocket clients.
- On shutdown, prevents new connections and waits for existing ones to close.
- Forces shutdown after 30 minutes if clients remain connected.