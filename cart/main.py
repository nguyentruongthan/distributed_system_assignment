from fastapi import FastAPI
import threading
import json
import uvicorn

import route
import config
from kafka_consumer import consumer, kafkaMessages
import define

app = FastAPI()
app.include_router(route.router)

def start_fastapi():
    uvicorn.run("main:app", host="0.0.0.0", port=config.CART_PORT, reload=False)

def start_consumer():
    global kafkaMessages
    print("Consumer start")
    try:
        for msg in consumer:
            print("from kafka: ", msg.value.decode("utf-8"))
            try:
                msg_json: dict = json.loads(msg.value)
                if msg_json["opcode"] == define.OP_CHECK_PRODUCT_QUANTITY_FAILED:
                    kafkaMessages[msg_json["id"]] = define.OP_CHECK_PRODUCT_QUANTITY_FAILED
                elif msg_json["opcode"] == define.OP_CHECK_USER_ACCOUNT_FAILED:
                    kafkaMessages[msg_json["id"]] = define.OP_CHECK_USER_ACCOUNT_FAILED
                elif msg_json["opcode"] == define.OP_CHECK_USER_ACCOUNT_SUCCESS:
                    kafkaMessages[msg_json["id"]] = define.OP_CHECK_USER_ACCOUNT_SUCCESS
            except json.JSONDecodeError as e:
                print("Parsed JSON: ", e)
            except KeyError as e:
                print(f"Key error: ", e)
            
    except KeyboardInterrupt:
        print("Consumer stopped.")
    finally:
        consumer.close()

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

    
