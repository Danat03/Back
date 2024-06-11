import json

from api.message.actions import get_messages
from api.message.websocket.socket import ConnectionManager

manager = ConnectionManager()

async def handle_messages(websocket, user, db, redis_messages):
    while True:
        data = await websocket.receive_text()
        parsed_data = json.loads(data)
        action = parsed_data.get("action")

        if action == "send_message":
            content = parsed_data.get("content")
            await manager.send_personal_message(content, websocket, db, redis_messages)
            await manager.broadcast_message(content, user.username, websocket)

        elif action == "load_more_messages":
            await load_more_messages(websocket, redis_messages)

async def load_more_messages(websocket, redis_messages):
    current_index = manager.last_message_index[websocket]
    new_start = current_index - 20
    more_messages = await get_messages(
        redis_pool_messages=redis_messages, start=new_start, count=20
    )
    await websocket.send_text(
        json.dumps({"type": "more_messages", "messages": more_messages})
    )
    manager.last_message_index[websocket] = new_start

async def handle_websocket_disconnect(user, websocket, db):
    await manager.disconnect(websocket, db)
    leave_message = f"Пользователь #{user.username} покинул чат."
    await manager.broadcast_message(
        leave_message, user.username, websocket, system_message=True
    )

async def handle_websocket_connect(user, websocket, db, redis_messages):
    await manager.connect(websocket, user, db, redis_messages)
    join_message = f"Пользователь #{user.username} вошел в чат."
    await manager.broadcast_message(
        join_message, user.username, websocket, system_message=True
    )
