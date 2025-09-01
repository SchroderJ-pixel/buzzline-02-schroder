# buzzline-02-schroder  

**Course:** Streaming Data – Module 2  
**Date:** September 1, 2025  
**Author:** Justin Schroder  
**GitHub:** [SchroderJ-pixel](https://github.com/SchroderJ-pixel) 

---

## Overview  

Streaming data is often too big for a single machine.  
Apache Kafka is a popular streaming platform that uses a publish–subscribe model:  

- **Producers** publish streaming data to topics  
- **Consumers** subscribe to topics and process the data in real time  

In this project, I built a **dungeon crawler producer** and a matching **consumer** to simulate real-time game events.  

---

## Task 1. Install and Start Kafka (WSL on Windows)  

Before starting, complete the setup steps in [buzzline-01-case](https://github.com/denisecase/buzzline-01-case).  
Python 3.11 is required.  

1. Install **Windows Subsystem for Linux (WSL)**  
2. Install the **Kafka streaming platform**  
3. Start the **Kafka service** (leave that terminal open)  

Detailed instructions: [SETUP_KAFKA](SETUP_KAFKA.md)  

---

## Task 2. Manage Local Virtual Environment  

From the project root folder in VS Code, create and activate your virtual environment. 

### Windows

Open PowerShell terminal in VS Code (Terminal / New Terminal / PowerShell).

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
py -m pip install --upgrade pip wheel setuptools
py -m pip install --upgrade -r requirements.txt
```

If you get execution policy error, run this first:
`Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

### Mac / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install --upgrade -r requirements.txt
```

## Task 3. Start a Kafka Producer  

Producers generate streaming data for our topics.  

### Windows  

```bash
.venv\Scripts\activate  
py -m producers.kafka_producer_schroder  
```

### Mac/Linux  
```
source .venv/bin/activate  
python3 -m producers.kafka_producer_schroder  
```

---

## Task 4. Start a Kafka Consumer  

Consumers process data from topics or logs in real time.  

In VS Code, open a NEW terminal in your root project folder.  

### Windows  

```bash
.venv\Scripts\activate  
py -m consumers.kafka_consumer_schroder  
```

### Mac/Linux  

```
source .venv/bin/activate  
python3 -m consumers.kafka_consumer_schroder  
```

---

## Example Output  
```
event: MOVE room:1 hp:100% gold:0 xp:0  
event: TRAP room:1 hp:100% gold:0 xp:0  
event: LOOT room:3 hp:100% gold:7 xp:0  
event: ENCOUNTER room:4 hp:100% gold:13 xp:0  
```

## Later Work Sessions

When resuming work on this project:

1. Open the folder in VS Code.
2. Start the Kafka service.
3. Activate your local project virtual environment (.venv).

## Save Space

To save disk space, you can delete the .venv folder when not actively working on this project.
You can always recreate it, activate it, and reinstall the necessary packages later.
Managing Python virtual environments is a valuable skill.

## License

This project is licensed under the MIT License as an example project.
You are encouraged to fork, copy, explore, and modify the code as you like.
See the [LICENSE](LICENSE.txt) file for more.
