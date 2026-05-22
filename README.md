# STAR AI Playwright MCP Demo

## 1. Überblick

Dieses Projekt ist ein Prototyp für eine **Smart Test Automation Runtime (STAR)**.

Die Idee des Prototyps ist, dass ein Benutzer eine Testanforderung in natürlicher Sprache eingibt. Eine echte AI erzeugt daraus strukturierte Testschritte. Diese Testschritte werden anschließend über einen **Playwright MCP Server** im Browser ausgeführt.

Der Prototyp zeigt damit, wie AI, MCP und Playwright gemeinsam für automatisierte UI-Tests genutzt werden können.

## 2. Ziel des Projekts

Ziel ist es, einen Testablauf nicht vollständig manuell als Playwright-Testcode schreiben zu müssen.

Stattdessen beschreibt der Benutzer den Test in natürlicher Sprache, zum Beispiel:

```text
Open http://localhost:3000 and take a screenshot named docker-test.
```

Oder:

```text
Open http://localhost:3000, fill username demo, fill password demo123, click the login button, verify that Dashboard is visible, and take a screenshot named login-success.
```

Aus dieser Beschreibung erzeugt die AI strukturierte Testschritte. Diese werden danach über den Playwright MCP Server ausgeführt.

## 3. Architektur

Die aktuelle Architektur sieht so aus:

```text
User / Browser
  ↓
Frontend
  ↓
Python-basierte STAR-Steuerzentrale
  ↓
AI Model
  ↓
JSON-Testschritte
  ↓
Playwright MCP Server
  ↓
Browser Automation mit Playwright
  ↓
Screenshot / Testergebnis
```

## 4. Komponenten

### 4.1 Frontend

Ordner:

```text
frontend/
```

Das Frontend stellt eine einfache Weboberfläche bereit.

Dort kann der Benutzer eine Testanforderung eingeben und mit dem Button **Run AI Test** starten.

Das Frontend läuft auf:

```text
http://localhost:3000
```

Außerdem enthält die Seite eine einfache Login-Demo mit:

```text
Username
Password
Login Button
Dashboard
```

Diese Login-Demo dient als Testobjekt.

### 4.2 Python-basierte STAR-Steuerzentrale

Ordner:

```text
python-api/
```

Die Python API ist die zentrale Orchestrierungsschicht.

Sie übernimmt folgende Aufgaben:

1. Testanforderung vom Frontend entgegennehmen
2. Testanforderung an die AI senden
3. Strukturierte JSON-Testschritte von der AI empfangen
4. Die JSON-Testschritte in MCP-Tool-Aufrufe übersetzen
5. Den Playwright MCP Server aufrufen
6. Testergebnis an das Frontend zurückgeben

Wichtige Dateien:

```text
api_server.py
ai_agent.py
requirements.txt
```

### 4.3 Playwright MCP Server

Ordner:

```text
mcp-server/
```

Der Playwright MCP Server stellt Browseraktionen als standardisierte MCP-Tools bereit.

Beispiele für solche Tools sind:

```text
browser_navigate
browser_type
browser_click
browser_wait_for
browser_take_screenshot
browser_snapshot
```

Der Python-Orchestrator ruft diese Tools auf. Der MCP Server führt die Aktionen anschließend mit Playwright im Browser aus.

## 5. AI-Integration

Im aktuellen Prototyp wird Gemini als echte AI verwendet.

Die AI bekommt eine natürlichsprachliche Testanforderung und erzeugt daraus strukturierte JSON-Testschritte.

Beispiel:

```text
Open http://localhost:3000 and take a screenshot named docker-test.
```

Mögliche AI-Ausgabe:

```json
[
  {
    "action": "goto",
    "url": "http://localhost:3000"
  },
  {
    "action": "screenshot",
    "name": "docker-test"
  }
]
```

Bei einem Login-Test kann die Ausgabe so aussehen:

```json
[
  {
    "action": "goto",
    "url": "http://localhost:3000"
  },
  {
    "action": "fill",
    "selector": "#username",
    "value": "demo"
  },
  {
    "action": "fill",
    "selector": "#password",
    "value": "demo123"
  },
  {
    "action": "click",
    "selector": "#login-button"
  },
  {
    "action": "expectText",
    "selector": "body",
    "value": "Dashboard"
  },
  {
    "action": "screenshot",
    "name": "login-success"
  }
]
```

Wichtig ist: Die AI führt den Browser nicht selbst aus. Sie erzeugt nur die Testschritte. Die Ausführung erfolgt über Python und den Playwright MCP Server.

## 6. Bezug zu Azure AI Foundry

In der Aufgabenstellung ist Microsoft Foundry beziehungsweise Azure AI Foundry als Zielplattform vorgesehen.

Im aktuellen Prototyp wird Gemini verwendet, weil kein direkter Zugriff auf Azure AI Foundry vorhanden ist.

Die Architektur ist jedoch so aufgebaut, dass Gemini später durch Azure AI Foundry ersetzt werden kann.

Aktueller Prototyp:

```text
Python-basierte STAR-Steuerzentrale
  ↓
Gemini
  ↓
JSON-Testschritte
  ↓
Playwright MCP Server
```

Zielarchitektur mit Azure AI Foundry:

```text
Python-basierte STAR-Steuerzentrale
  ↓
Azure AI Foundry Agent
  ↓
Playwright MCP Server
  ↓
Browser Automation
```

Damit bleibt der Playwright MCP Server weiterhin die zentrale Komponente für die Browserautomatisierung.

## 7. Projektstruktur

```text
star-ai-playwright-demo/
├── frontend/
│   ├── index.html
│   └── Dockerfile
├── python-api/
│   ├── api_server.py
│   ├── ai_agent.py
│   ├── requirements.txt
│   └── Dockerfile
├── mcp-server/
│   └── Dockerfile
├── test-results/
├── docker-compose.yml
├── mcp-config.json
├── .env
└── README.md
```

## 8. Voraussetzungen

Für die Ausführung werden benötigt:

```text
Docker
Docker Compose
Gemini API Key
```

## 9. Environment-Konfiguration

Im Projekt-Hauptordner muss eine `.env`-Datei liegen.

Beispiel:

```env
GEMINI_API_KEY=your_api_key_here
```

Der echte API-Key darf nicht in Git eingecheckt werden.

Die `.env`-Datei sollte deshalb in `.gitignore` eingetragen sein.

## 10. Projekt starten

Im Projekt-Hauptordner ausführen:

```bash
docker compose up --build
```

Danach sind die Komponenten erreichbar unter:

```text
Frontend:              http://localhost:3000
Python API:            http://localhost:8080
Playwright MCP Server: http://localhost:8931/mcp
```

## 11. Beispieltest: Login

Im Frontend kann folgender Login-Test eingegeben werden:

```text
Open http://localhost:3000, fill username demo, fill password demo123, click the login button, verify that Dashboard is visible, and take a screenshot named login-success.
```

Erwarteter Ablauf:

```text
1. Webseite öffnen
2. Username ausfüllen
3. Passwort ausfüllen
4. Login-Button klicken
5. Dashboard-Text prüfen
6. Screenshot speichern
```

Erwarteter Screenshot:

```text
test-results/login-success.png
```

## 12. Erlaubte Aktionen

Der Prototyp unterstützt aktuell nur eine begrenzte Menge an Aktionen.

Erlaubte Aktionen:

```text
goto
fill
click
expectText
screenshot
```

Diese Begrenzung ist bewusst gewählt. Sie sorgt dafür, dass die AI nicht beliebige oder gefährliche Aktionen ausführen kann.

## 13. Sicherheit und Einschränkungen

Der Prototyp ist nur für Demonstrationszwecke gedacht.

Nicht vorgesehen sind:

```text
Tests gegen Produktivsysteme
Nutzung echter Zugangsdaten
Verarbeitung personenbezogener Daten
Destruktive Aktionen
Unkontrollierte Browseraktionen
```

Für eine produktive Nutzung müssten zusätzliche Sicherheitsmechanismen ergänzt werden, zum Beispiel:

```text
URL-Allowlist
Validierung der AI-generierten Schritte
Logging
Review-Freigabe für kritische Aktionen
Rollen- und Rechtekonzept
Testdatenmanagement
```

## 14. Aktueller Status

Der aktuelle Prototyp zeigt erfolgreich folgenden Ablauf:

```text
Frontend
  ↓
Python-basierte STAR-Steuerzentrale
  ↓
AI
  ↓
JSON-Testschritte
  ↓
Playwright MCP Server
  ↓
Browser
  ↓
Screenshot / Testergebnis
```

Damit wurde die Grundidee einer MCP-basierten Smart Test Automation Runtime demonstriert.

## 15. Nächste Ausbauschritte

Mögliche nächste Schritte sind:

```text
1. Gemini durch Azure AI Foundry ersetzen
2. Azure AI Foundry Agent direkt mit dem Playwright MCP Server verbinden
3. Logging und Reporting erweitern
4. Validierung der AI-generierten Schritte verbessern
5. URL-Allowlist ergänzen
6. CI/CD-Integration aufbauen
7. Wiederverwendbare Testvorlagen definieren
8. Testausführung für komplexere Webseiten erweitern
```
