# Systemdokumentation
## 1. Klassendiagramm (Automatisch aus Quellcode generiert)
```mermaid
classDiagram
    class Gesamtsystem {
        +Lokales_Steuergerat
        +Remote_Infrastruktur
    }
    class Lokales_Steuergerat {
        <<Subsystem HW>>
        +Sensoren
        +Python_Runtime
        +Physisches_Relais
    }
    class Python_Runtime {
        <<Subsystem SW>>
        +SafetyCriticalClient
        +Pydantic_Validators
    }
    class Remote_Infrastruktur {
        <<Subsystem Cloud>>
        +API_Gateway
        +KI_Modell_vLLM
    }
    Gesamtsystem *-- Lokales_Steuergerat
    Gesamtsystem *-- Remote_Infrastruktur
    Lokales_Steuergerat *-- Python_Runtime
    Remote_Infrastruktur *-- KI_Modell_vLLM
```
## 2. Internes Blockdiagramm (Signalfluss)
```mermaid
flowchart TB
    subgraph local [Lokales System]
        sensor[Sensoren]
        python[Python Client]
        fallback[Safe State Relais]
    end
    subgraph cloud [Cloud Server]
        gateway[API Gateway]
        model[KI Modell]
    end
    sensor -- Sensor-Daten --> python
    python -- HTTPS / JSON --> gateway
    gateway -- Inferenz-Request --> model
    python -- Not-Aus Signal --> fallback
```
## 3. Sequenzdiagramm (Timeout & Fallback)
```mermaid
sequenceDiagram
    autonumber
    participant S as Sensor / Anlage
    participant C as Lokaler Python Client
    participant K as Remote KI-Server
    S->>C: Sende aktuelle Messwerte (z.B. Temp=45°C)
    Note over C: Input-Validierung via Pydantic
    C->>K: HTTP POST /v1/analyze (Starte Timer: t=0.0s)
    Note over K: Server blockiert / Netzwerk-Latenz...
    Note over C: Timer läuft ab (t=1.0s)<br/>Strikter Timeout erreicht!
    Note over C: C bricht Verbindung autonom ab
    C->>C: Aktiviere _trigger_safe_state()
    C->>S: Notfall-Kommando: Fahre Anlage in sicheren Zustand!
    opt Späte Antwort vom Server
        K--xC: Antwort (wird vom Client ignoriert/abgewiesen)
    end
```
## 4. Zustandsdiagramm (Safety States)
```mermaid
stateDiagram-v2
    [*] --> Initialisierung
    Initialisierung --> Normalbetrieb : Selbsttest erfolgreich
    Initialisierung --> Sicherer_Zustand : Selbsttest fehlgeschlagen
    state Normalbetrieb {
        [*] --> Warte_auf_Daten
        Warte_auf_Daten --> Sende_API_Request : Daten empfangen
        Sende_API_Request --> Verarbeite_KI_Antwort : HTTP 200 OK
    }
    Normalbetrieb --> Sicherer_Zustand : Event: Timeout (1s)
    Normalbetrieb --> Sicherer_Zustand : Event: API-Fehler (500/401)
    Normalbetrieb --> Sicherer_Zustand : Event: Datenkorruption (Validation Error)
    Normalbetrieb --> Kritischer_Eingriff : KI meldet "status=RISK"
    Kritischer_Eingriff --> Normalbetrieb : Gefahr abgewendet
    Kritischer_Eingriff --> Sicherer_Zustand : System reagiert nicht
    state Sicherer_Zustand {
        [*] --> Lokaler_Notbetrieb
        Lokaler_Notbetrieb --> Regelabschaltung
    }
    Sicherer_Zustand --> [*] : System aus
```
