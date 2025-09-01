"""
kafka_producer_schroder.py

Produce dungeon-crawler events (JSON strings) and send them to a Kafka topic.
"""

#####################################
# Import Modules
#####################################

# Standard Library
import json
import os
import sys
import time
import random
from datetime import datetime

# External
from dotenv import load_dotenv

# Local utils
from utils.utils_producer import (
    verify_services,
    create_kafka_producer,
    create_kafka_topic,
)
from utils.utils_logger import logger


#####################################
# Getter Functions for .env Variables
#####################################

def get_kafka_topic() -> str:
    topic = os.getenv("KAFKA_TOPIC", "dungeon_topic")
    logger.info(f"Kafka topic: {topic}")
    return topic


def get_message_interval() -> float:
    raw = os.getenv("MESSAGE_INTERVAL_SECONDS", "1")
    try:
        interval = float(raw)
    except ValueError:
        interval = 1.0
    logger.info(f"Message interval: {interval} seconds")
    return interval


#####################################
# Message Generator
#####################################

def now_iso() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def generate_messages(producer, topic, interval_secs: float):
    """
    Generate a stream of dungeon crawler messages and send them to Kafka.
    """
    enemies = ["Goblin", "Skeleton", "Mimic", "Slime", "Bat"]
    loot = ["Potion", "Silver Coin", "Gem", "Ancient Relic"]
    rooms = 1

    try:
        while True:
            event_type = random.choice(["MOVE", "ENCOUNTER", "LOOT", "TRAP"])
            if event_type == "MOVE":
                msg = {
                    "ts": now_iso(),
                    "event": "MOVE",
                    "room": rooms,
                    "direction": random.choice(["N", "S", "E", "W"]),
                }
                rooms += 1
            elif event_type == "ENCOUNTER":
                msg = {
                    "ts": now_iso(),
                    "event": "ENCOUNTER",
                    "enemy": random.choice(enemies),
                    "damage": random.randint(5, 20),
                }
            elif event_type == "LOOT":
                msg = {
                    "ts": now_iso(),
                    "event": "LOOT",
                    "item": random.choice(loot),
                    "gold": random.randint(1, 50),
                }
            else:  # TRAP
                msg = {
                    "ts": now_iso(),
                    "event": "TRAP",
                    "trap": random.choice(["Spikes", "Poison Dart", "Falling Rock"]),
                    "damage": random.randint(3, 15),
                }

            json_str = json.dumps(msg)
            logger.info(f"Generated dungeon event: {json_str}")
            producer.send(topic, value=json_str)
            logger.info(f"Sent message to topic '{topic}': {msg['event']}")
            time.sleep(interval_secs)

    except KeyboardInterrupt:
        logger.warning("Producer interrupted by user.")
    except Exception as e:
        logger.error(f"Error in message generation: {e}")
    finally:
        producer.close()
        logger.info("Kafka producer closed.")


#####################################
# Main Function
#####################################

def main():
    logger.info("START dungeon producer (schroder).")
    load_dotenv()
    verify_services()

    topic = get_kafka_topic()
    interval_secs = get_message_interval()

    producer = create_kafka_producer()
    if not producer:
        logger.error("Failed to create Kafka producer. Exiting...")
        sys.exit(3)

    try:
        create_kafka_topic(topic)
        logger.info(f"Kafka topic '{topic}' is ready.")
    except Exception as e:
        logger.error(f"Failed to create or verify topic '{topic}': {e}")
        sys.exit(1)

    logger.info(f"Starting dungeon crawl message production to topic '{topic}'...")
    generate_messages(producer, topic, interval_secs)

    logger.info("END producer.")


#####################################
# Conditional Execution
#####################################

if __name__ == "__main__":
    main()
