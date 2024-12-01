from kafka import KafkaProducer
import config

producer = KafkaProducer(
    bootstrap_servers = f"{config.KAFKA_BOOTSTRAP_SERVER}"
)