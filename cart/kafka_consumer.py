from kafka import KafkaConsumer
import config

consumer = KafkaConsumer(
    *[config.KAFKA_TOPIC],
    bootstrap_servers=f'{config.KAFKA_BOOTSTRAP_SERVER}',
    auto_offset_reset='latest'
)

kafkaMessages: dict = dict()

if __name__ == "__main__":
    print("Consumer start")
    try:
        for msg in consumer:
            print(msg.value.decode("utf-8"))
    except KeyboardInterrupt:
        print("Consumer stopped.")
    finally:
        consumer.close()

