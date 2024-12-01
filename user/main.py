import threading
import asyncio
from fastapi import FastAPI
import uvicorn
import json

import route
import config
from kafka_consumer import consumer
import define
import service

app = FastAPI()
app.include_router(route.router)

def start_fastapi():
    uvicorn.run("main:app", host="0.0.0.0", port=config.USER_PORT, reload=False)

def start_consumer():
    async def consumer_handler():
        print("Consumer started")
        try:
            for msg in consumer:
                print("from kafka:", msg.value.decode("utf-8"))
                try:
                    msg_json: dict = json.loads(msg.value.decode("utf-8"))
                    if msg_json["opcode"] == define.OP_CHECK_PRODUCT_QUANTITY_SUCCESS:
                        await service.checkoutCart(msg_json)
                except json.JSONDecodeError as e:
                    print("JSON parsing error:", e)
                except KeyError as e:
                    print("Key error:", e)
        except KeyboardInterrupt:
            print("Consumer stopped.")
        finally:
            consumer.close()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(consumer_handler())
    loop.close()

if __name__ == "__main__":
    # Tạo thread cho FastAPI
    fastapi_thread = threading.Thread(target=start_fastapi, daemon=True)
    # Tạo thread cho Kafka Consumer
    consumer_thread = threading.Thread(target=start_consumer, daemon=True)

    # Start cả hai threads
    fastapi_thread.start()
    consumer_thread.start()

    # Giữ chương trình chính hoạt động để threads không kết thúc
    fastapi_thread.join()
    consumer_thread.join()
