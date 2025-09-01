"""
kafka_consumer_schroder.py

Consume dungeon-crawler JSON messages from a Kafka topic and perform simple
real-time analytics (low HP alerts, boss spawn/defeat, death, jackpot loot).
"""

#####################################
# Import Modules
#####################################

# Standard Library
import json
import os
from collections import defaultdict
from typing import Dict, Any, DefaultDict

# External packages
from dotenv import load_dotenv

# Local utils
from utils.utils_consumer import create_kafka_consumer
from utils.utils_logger import logger


#####################################
# Load Environment Variables
#####################################

load_dotenv()


#####################################
# Getter Functions for .env Variables
#####################################

def get_kafka_topic() -> str:
    topic = os.getenv("KAFKA_TOPIC", "dungeon_topic")
    logger.info(f"Kafka topic: {topic}")
    return topic


def get_kafka_consumer_group_id() -> str:
    group_id: str = os.getenv("KAFKA_CONSUMER_GROUP_ID_JSON", "schroder_group")
    logger.info(f"Kafka consumer group id: {group_id}")
    return group_id


def get_low_hp_threshold() -> int:
    try:
        return int(os.getenv("LOW_HP_THRESHOLD", "25"))
    except ValueError:
        return 25


def get_jackpot_gold_threshold() -> int:
    try:
        return int(os.getenv("JACKPOT_GOLD_THRESHOLD", "120"))
    except ValueError:
        return 120


#####################################
# Analytics State
#####################################

RunState = Dict[str, Any]
state: DefaultDict[str, RunState] = defaultdict(lambda: {
    "hp": 100,
    "gold": 0,
    "xp": 0,
    "rooms": 0,
    "boss_seen": False,
    "alerts": 0,
})

LOW_HP = get_low_hp_threshold()
JACKPOT = get_jackpot_gold_threshold()


#####################################
# Define a function to process a single message
#####################################

def process_message(message: str) -> None:
    """
    Process a single message.

    Expects JSON strings produced by kafka_producer_schroder.py, e.g.:
      {"ts":"...","run_id":"run-...","event":"ENCOUNTER","room":3,"hp":84,...}
    """
    try:
        evt = json.loads(message)
        if not isinstance(evt, dict) or "event" not in evt:
            logger.info(f"Processing message (non-dungeon format): {message}")
            return
    except json.JSONDecodeError:
        logger.info(f"Processing message (not JSON): {message}")
        return

    run_id = str(evt.get("run_id", "unknown"))
    st = state[run_id]

    # Update core stats
    st["hp"] = int(evt.get("hp", st["hp"]))
    st["gold"] = int(evt.get("gold", st["gold"]))
    st["xp"] = int(evt.get("xp", st["xp"]))
    st["rooms"] = max(st["rooms"], int(evt.get("room", st["rooms"])))

    # Alerts based on event & thresholds
    name = evt.get("event", "UNKNOWN")

    if name == "BOSS_INTRO" and not st["boss_seen"]:
        st["boss_seen"] = True
        boss = evt.get("details", {}).get("boss") or evt.get("boss", "???")
        logger.warning(f"[ALERT] {run_id}: Boss appeared - {boss} (room {evt.get('room')})")
        st["alerts"] += 1

    if name == "BOSS_DEFEATED":
        logger.warning(f"[ALERT] {run_id}: Boss defeated. Run success")
        st["alerts"] += 1

    if name == "DEATH":
        cause = evt.get("details", {}).get("cause") or evt.get("cause", "unknown")
        logger.warning(f"[ALERT] {run_id}: Player died (cause: {cause})")
        st["alerts"] += 1

    if name == "LOOT":
        details = evt.get("details", {})
        found = int(details.get("gold_found", details.get("gold", 0)))
        if found >= JACKPOT:
            logger.warning(f"[ALERT] {run_id}: Jackpot loot found (+{found} gold)")
            st["alerts"] += 1

    if st["hp"] <= LOW_HP:
        logger.warning(f"[ALERT] {run_id}: Low HP {st['hp']}%")
        st["alerts"] += 1

    # Rolling summary (info-level)
    summary = f"[{run_id}] event:{name} room:{st['rooms']} hp:{st['hp']}% gold:{st['gold']} xp:{st['xp']} alerts:{st['alerts']}"
    logger.info(summary)


#####################################
# Define main function for this module
#####################################

def main() -> None:
    logger.info("START consumer (schroder).")

    topic = get_kafka_topic()
    group_id = get_kafka_consumer_group_id()
    logger.info(f"Consumer: Topic '{topic}' and group '{group_id}'...")

    consumer = create_kafka_consumer(topic, group_id)

    logger.info(f"Polling messages from topic '{topic}'...")
    try:
        for msg in consumer:
            value = msg.value
            if isinstance(value, (bytes, bytearray)):
                value = value.decode("utf-8", errors="replace")
            process_message(value)
    except KeyboardInterrupt:
        logger.warning("Consumer interrupted by user.")
    except Exception as e:
        logger.error(f"Error while consuming messages: {e}")
    finally:
        consumer.close()
        logger.info(f"Kafka consumer for topic '{topic}' closed.")

    logger.info(f"END consumer for topic '{topic}' and group '{group_id}'.")
    

#####################################
# Conditional Execution
#####################################

if __name__ == "__main__":
    main()
