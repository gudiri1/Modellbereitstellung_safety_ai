import asyncio
import logging
import httpx
from pydantic import BaseModel, Field, ValidationError

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Strukturierte Antwort-Klasse
class SafetyResponse(BaseModel):
    status: str
    confidence: float
    action_required: bool

class SafetyCriticalClient:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {token}"}
        # In sicherheitskritischen Systemen zählen Millisekunden
        self.timeout = httpx.Timeout(1.0) 

    async def send_data(self, temp: float, press: float, force_timeout: bool = False) -> SafetyResponse:
        url = f"{self.base_url}/v1/analyze"
        payload = {"temperature": temp, "pressure": press, "simulate_delay": force_timeout}

        async with httpx.AsyncClient(headers=self.headers, timeout=self.timeout) as client:
            try:
                response = await client.post(url, json=payload)
                
                # Prüfe HTTP-Status (z.B. 401 oder 500)
                response.raise_for_status()
                
                # Versuche die Antwort strikt gegen das Schema zu validieren
                return SafetyResponse(**response.json())

            except httpx.TimeoutException:
                logging.error("❌ TIMEOUT: Server antwortet nicht schnell genug!")
                return self._trigger_safe_state("Server-Verzögerung")
            except httpx.HTTPStatusError as e:
                logging.error(f"❌ HTTP FEHLER: Server meldet Status {e.response.status_code}")
                return self._trigger_safe_state("Authentifizierung / Serverfehler")
            except (ValidationError, ValueError) as e:
                logging.error(f"❌ KORRUPTE DATEN: KI liefert ungültiges Format! {e}")
                return self._trigger_safe_state("Daten-Integritätsfehler")
            except Exception as e:
                logging.error(f"❌ NETZWERKFEHLER: Keine Verbindung zum Server möglich. {e}")
                return self._trigger_safe_state("Verbindungsverlust")

    def _trigger_safe_state(self, reason: str) -> SafetyResponse:
        """Deterministischer, lokaler Notfall-Zustand (Fail-Safe)"""
        logging.warning(f"⚠️ Aktiviere lokalen Notfallmodus (Safe State). Grund: {reason}")
        return SafetyResponse(status="EMERGENCY_FALLBACK", confidence=1.0, action_required=True)

# Simulation verschiedener Szenarien
async def main():
    client = SafetyCriticalClient(base_url="http://127.0.0.1:8000", token="SAFE_TOKEN_123")

    print("\n--- 1. Normaler Betrieb (Sicherer Zustand) ---")
    res = await client.send_data(temp=45.0, press=1.0)
    print(f"Resultat: {res.json()}\n")

    print("--- 2. Kritische Werte (KI erkennt Gefahr) ---")
    res = await client.send_data(temp=120.0, press=2.5)
    print(f"Resultat: {res.json()}\n")

    print("--- 3. Server-Verzögerung (Client erzwingt Timeout-Schutz) ---")
    res = await client.send_data(temp=45.0, press=1.0, force_timeout=True)
    print(f"Resultat: {res.json()}\n")

if __name__ == "__main__":
    asyncio.run(main())
