# Anodizing Digital Twin

## Industry 4.0 Demonstration Project

This project is a **Digital Twin / virtual process simulation** of an industrial aluminium anodizing line, developed as an **Industry 4.0 demonstration and R\&D engineering tool**.

The project combines a Python-based process model with a browser-based HMI/SCADA-style interface. It demonstrates how process equipment, sensor data, process calculations, alarms, disturbances and quality inspection can be represented in a connected digital environment.

> \*\*Important:\*\* This is a simulation and engineering demonstration. It is not a production PLC/SCADA control system. Process values, alarms, QC results and equipment behavior are simulated and must be calibrated and validated against actual plant data before industrial deployment.

\---

## Industry 4.0 Concept

The project demonstrates several core Industry 4.0 concepts:

* **Digital Twin** – virtual representation of an anodizing process and its equipment.
* **Cyber-physical system concept** – physical-process elements are represented by software models and simulated telemetry.
* **Industrial HMI / SCADA** – browser-based visualization of process status and equipment.
* **Real-time monitoring** – live temperature, level, flow, current, voltage, power and process status.
* **Process simulation** – virtual anodizing, coloring, sealing and associated process behavior.
* **Predictive process modeling** – simplified oxide-thickness prediction using process parameters and Faraday-law-based calculations.
* **Disturbance simulation** – intentional process deviations can be injected to demonstrate abnormal conditions.
* **Alarm management** – high temperature, low level, low flow, current deviation and thickness-related alarms/warnings.
* **Quality integration** – simulated QC inspection for coating thickness, gloss, color ΔE and sealing.
* **Data connectivity** – Python and the web HMI communicate through WebSocket telemetry.
* **Future-ready architecture** – the simulation can be extended toward PLC, OPC UA, MQTT, database and real sensor integration.

\---

## Process Represented

The digital twin represents a simplified anodizing line including:

1. Loading
2. Degreasing
3. Water Wash 1
4. Chemical Polishing
5. Water Wash 2
6. Neutralization
7. Water Wash 3
8. DC Anodizing
9. Water Wash 4
10. Coloring
11. Water Wash 5
12. Sealing
13. Hot Water Wash
14. Unloading
15. QC Inspection

\---

## Main Features

### Digital Twin / Process Model

* Virtual batch processing
* Process station sequencing
* Bath temperature behavior
* Electrolyte level and circulation flow
* Rectifier voltage/current behavior
* Current density calculation
* Power calculation
* Simplified anodic oxide growth prediction
* Predicted final coating thickness

### HMI / SCADA Visualization

* Industrial-style process dashboard
* Virtual anodizing tank
* Rack and multiple rims
* Live process instrumentation
* Equipment status indicators
* Temperature and process trends
* Batch information
* Process target values

\---

## Software Architecture

```text
                    ┌─────────────────────────┐
                    │   Browser HMI / SCADA   │
                    │      web/index.html     │
                    └────────────┬────────────┘
                                 │
                          WebSocket telemetry
                                 │
                    ┌────────────▼────────────┐
                    │     Python Backend      │
                    │        server.py        │
                    └────────────┬────────────┘
                                 │
               ┌─────────────────┴─────────────────┐
               │                                   │
     ┌─────────▼─────────┐              ┌─────────▼─────────┐
     │  Process Model    │              │ Process Config    │
     │ process\_model.py  │              │process\_config.py  │
     └───────────────────┘              └───────────────────┘
```

### Files

```text
Anodizing\_Digital\_Twin/
│
├── README.md
├── requirements.txt
├── .gitignore
├── server.py
├── process\_model.py
├── process\_config.py
├── web/
│   └── index.html
└── data/
```

### File Purpose

|File|Purpose|
|-|-|
|`server.py`|Runs the digital-twin simulation and WebSocket server|
|`process\_model.py`|Process calculations such as area, current density, power and simplified oxide growth|
|`process\_config.py`|Process recipes, targets, QC limits and station configuration|
|`web/index.html`|Browser-based HMI / SCADA visualization|
|`requirements.txt`|Python dependency list|
|`.gitignore`|Prevents temporary/cache files from being committed|

\---

## Requirements

* Python 3.10+ recommended
* Modern web browser such as Chrome or Edge
* Internet connection is **not required for the simulation after dependencies are installed**

Install the Python dependency:

```bash
python -m pip install -r requirements.txt
```

\---

## Running the Digital Twin

### Windows PowerShell

```powershell
cd DID\_Anodizing\_Digital\_Twin\_V3
python -m pip install -r requirements.txt
python server.py
```

Then open:

```text
web/index.html
```

in a browser and click **CONNECT**.

The Python backend runs the simulated process and sends telemetry to the HMI through WebSocket.

\---

## How the Simulation Works

1. A virtual batch is created.
2. The process moves through the configured stations.
3. The anodizing stage calculates current, current density, power and simulated oxide growth.
4. Temperature, level and flow are continuously simulated.
5. The HMI receives telemetry from the Python backend.
6. Disturbances can be injected manually.
7. Alarm logic evaluates the simulated process condition.
8. During coloring, the rim visual changes according to the selected coloring method.
9. At the QC stage, simulated thickness, gloss, ΔE and sealing results are generated.
10. The batch receives an overall PASS / FAIL result.

\---

## Future Industry 4.0 Extensions

The current project is intentionally a simulation. A future industrial implementation could connect the digital twin to actual plant systems, for example:

```text
Physical Plant
     │
     ├── Temperature Sensor
     ├── Level Sensor
     ├── Flow Sensor
     ├── Rectifier
     ├── PLC
     └── QC Instruments
            │
            ▼
     OPC UA / MQTT / Industrial Ethernet
            │
            ▼
      Digital Twin Platform
            │
      ┌─────┼─────────────┐
      ▼     ▼             ▼
     HMI  Historian   Analytics / AI
                         │
                         ▼
                  Predictive Quality
```

Potential future features include:

* PLC/SCADA connectivity
* OPC UA or MQTT communication
* Real sensor acquisition
* Historical batch database
* Batch traceability
* Recipe management
* Actual-vs-predicted comparison
* Predictive quality analytics
* Predictive maintenance
* OEE monitoring
* Energy monitoring
* Automatic report generation
* Machine-learning-based quality prediction
* Cloud or edge deployment

\---

## Important Engineering Note

The simplified Faraday-law calculation is intended for **demonstration and model development**. Actual anodic oxide thickness depends on factors including current efficiency, bath chemistry, temperature, alloy condition, current distribution, agitation and process time.

The model should therefore be calibrated using actual production/trial data before being used for process prediction or decision-making.

Similarly, the current surface area, process targets, alarm limits and QC limits in the configuration are demonstration parameters unless explicitly replaced with approved plant specifications.

\---

## Author / Project

Developed by Vaibhav Gupta as an R\&D / Industry 4.0 engineering demonstration project.

**Technology:** Python • WebSocket • HTML • CSS • JavaScript • Process Simulation • HMI/SCADA Concepts • Digital Twin

