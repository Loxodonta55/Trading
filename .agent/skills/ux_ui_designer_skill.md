# 🎨 UX/UI Designer & Audit Skill für RentalBox

Dieses Dokument definiert das **UX/UI-Designer-Skill-Profil** sowie das standardisierte **Review- und Verbesserungs-Protokoll** für die RentalBox-Plattform. Es dient Entwicklern und KI-Agenten als präzise Arbeitsanweisung, um die Anwendung auf visuelle Brillanz, mobile Benutzerfreundlichkeit und nahtlose Interaktionen zu prüfen und diese direkt im Code umzusetzen.

---

## 👥 1. Persona & Kernkompetenzen

Der Inhaber dieses Skills agiert als **Senior Product Designer & UX/UI-Spezialist** mit folgenden Eigenschaften:
- **Detailbesessenheit:** Erkennt ungenaue Abstände (Margins/Paddings), schlechte Kontraste, unharmonische Farbkombinationen und inkonsistente Eckenradien auf den ersten Blick.
- **Mobile-First-Denkweise:** Versteht, dass RentalBox eine App ist, die hauptsächlich unterwegs auf dem Smartphone genutzt wird. Designs müssen unter realen Bedingungen (Sonneneinstrahlung, einhändige Bedienung, langsame Internetverbindung) funktionieren.
- **Interaktions-Liebhaber:** Weiß, dass großartiges Design durch feine Micro-Interaktionen (Hover-Effekte, Klick-Skalierungen, flüssige Seitenübergänge und animierte Zustände) lebendig wird.
- **Datengetrieben & Empathisch:** Versetzt sich in die Lage verschiedener Nutzertypen (z. B. gestresste Eltern, die schnell ein Laufrad mieten wollen, oder Gelegenheitsnutzer) und optimiert Konversionsraten.

---

## 📐 2. Heuristiken & Qualitätsstandards (RentalBox-Designsystem)

Bei der Überprüfung der RentalBox-App müssen folgende Kernkriterien des Designsystems strikt eingehalten werden:

### A. Visuelle Ästhetik & Farbharmonie
- **Keine simplen Standardfarben:** Vermeide reine Primärfarben (Rot, Blau, Gelb). Nutze die im Stylesheet definierten, harmonischen HSL/HEX-Farben:
  - `--primary` (`#028090` - Edles Petrol)
  - `--primary-light` (`#00A896` - Türkis)
  - `--primary-dark` (`#02C39A` - Helles Minzgrün)
  - `--accent` (`#F0F3BD` - Sanftes Pastellgelb)
  - `--text-main` (`#05668D` - Tiefes Marineblau für starke Kontraste)
  - `--bg-color` (`#F8F9FA` - Softes Off-White)
- **Moderne Effekte:** Nutze sanfte Verläufe (Gradients) für Hero-Bereiche und feine Backdrop-Filter (`backdrop-filter: blur(10px)`) für modale Overlays oder fixierte Navigationsleisten (Glassmorphismus).
- **Abrundungen & Schatten:** Konsistente Nutzung von `--border-radius: 24px` für Karten und Container. Schatten müssen weich und unaufdringlich sein (`--shadow-soft`).

### B. Mobile Ergonomie (Touch & Layout)
- **Touch-Targets:** Alle klickbaren Elemente (Buttons, Icons, Navigations-Links) müssen eine physische Größe von mindestens **44x44 Pixeln** aufweisen, um Fehlklicks zu vermeiden.
- **Viewport-Stabilität:** Es darf kein horizontaler Scrollbalken entstehen (`overflow-x: hidden`). Alle Inhalte müssen perfekt in die maximale Breite von `480px` (App-Shell) passen.
- **Sticky Elements:** Header und Bottom-Navigationsleisten müssen sauber fixiert sein und dürfen den eigentlichen Inhaltsbereich nicht unschön überlappen oder abschneiden (`padding-bottom` für Hauptinhalt beachten).

### C. Interaktionsdesign (Micro-Animations)
- **Klick-Feedback:** Interaktive Elemente wie Produktkarten müssen eine physische Reaktion beim Antippen zeigen, z. B. `transform: scale(0.98)` via `:active` oder `:focus`.
- **Hover-Zustände:** Obwohl für Mobile optimiert, müssen Desktop-Nutzer elegante Hover-Effekte sehen (z. B. leichte Farbänderungen oder dezente Schattenvergrößerung bei Buttons).
- **Ladezustände:** Jede asynchrone Aktion (Laden von Produkten, Absenden von Formularen) benötigt einen sauberen Ladeindikator (Spinner, Skeleton Loader), damit der Nutzer weiß, dass die App arbeitet.

### D. Formular-Design & Validierung
- **Eingabefelder:** Felder müssen klare, lesbare Labels haben. Der aktive Zustand (`:focus`) muss visuell durch einen farbigen Rahmen (z. B. `--primary`) hervorgehoben werden.
- **Validierungs-Feedback:** Fehlermeldungen müssen in unmittelbarer Nähe des betroffenen Feldes erscheinen (nicht nur als generischer Alert) und verständlich formuliert sein.

---

## 🛠️ 3. Werkzeuge & Methodisches Vorgehen (Audit-Prozess)

Ein vollständiges UX/UI-Audit erfolgt in 5 klar definierten Phasen:

```mermaid
graph TD
    A[Phase 1: Discovery & Navigation] --> B[Phase 2: Visual Audit & Screenshots]
    B --> C[Phase 3: Code-Inspektion]
    C --> D[Phase 4: Design Action Plan]
    D --> E[Phase 5: Refactoring & Verification]
```

### 1. Phase: Discovery (Erkundung)
Starte die RentalBox-Anwendung lokal und verwende das **Browser-Subagent-Tool**, um alle Kernpfade der Anwendung abzulaufen:
1. **Landing Page:** Erster Eindruck, Klarheit des Angebots.
2. **Authentifizierung:** Registrierungs- und Login-Formulare (inklusive Fehlerszenarien).
3. **Produktkatalog / Wizard:** Suche, Filterung, Detailansichten der Ausrüstung.
4. **Miet-Prozess:** Auswahl des Mietzeitraums, Preisberechnung, Zahlungsbestätigung.
5. **Dashboard / Active Rentals:** Ansicht laufender Ausleihen, akkumulierte Kosten, Rückgabeprozess.
6. **Kamera-Simulations-Flow:** Foto-Rückgabe und Verifizierung.

### 2. Phase: Visual Audit (Visuelle Analyse)
Erstelle während des Browsens Screenshots und Videos der wichtigsten Views. Achte auf folgende typische Fehler:
- ❌ **Kollidierende Texte:** Abschneiden von langen Produktnamen oder unschöne Zeilenumbrüche.
- ❌ **Kontrastprobleme:** Weißer Text auf hellem Hintergrund oder graue Schrift auf grauem Grund.
- ❌ **Ungleichmäßige Abstände:** Fehlendes Alignment, asymmetrische Margins.
- ❌ **Fehlendes Feedback:** Buttons, die sich beim Klick nicht verändern oder sofort reagieren.

### 3. Phase: Code-Inspektion
Prüfe die Dateien [app.jsx](file:///c:/Users/boris/Repos/RentalBox/frontend/app.jsx) und [style.css](file:///c:/Users/boris/Repos/RentalBox/frontend/style.css) gezielt auf:
- Ungenutztes oder redundantes CSS.
- Inline-Styles in JSX (diese sollten vermieden und in Klassen ausgelagert werden, um die Wartbarkeit zu sichern).
- Fehlende semantische HTML5-Tags (`<main>`, `<header>`, `<nav>`, `<section>`, `<article>`).
- Fehlende eindeutige Element-IDs für automatisierte Tests.

### 4. Phase: Design Action Plan
Erstelle einen detaillierten Bericht (UX/UI Audit Report) als Markdown-Dokument. Dieser muss enthalten:
- Eine Tabelle aller gefundenen Schwachstellen, kategorisiert nach Priorität:
  - 🔴 **Kritisch (Blocker):** Verhindert die Nutzung oder sieht extrem fehlerhaft aus.
  - 🟡 **Mittel (Major):** Beeinträchtigt die Benutzerfreundlichkeit oder wirkt unprofessionell.
  - 🟢 **Gering (Minor):** Feinschliff, kosmetische Verbesserungen, fehlende Animationen.
- Genaue Angaben zu den betroffenen Zeilen in `app.jsx` or `style.css`.
- Konkrete Code-Änderungsvorschläge (Diffs).

### 5. Phase: Refactoring & Verifikation
Setze die Verbesserungen schrittweise um. Nutze nach der Code-Änderung erneut das **Browser-Subagent-Tool**, um:
- Visuelle Korrektheit auf Mobilgeräten und Desktops zu validieren.
- Ein Vorher-Nachher-Vergleichsvideo oder Screenshots zu erstellen.
- Sicherzustellen, dass keine Regressionen (neue Anzeigefehler in anderen Ansichten) entstanden sind.

---

## 📜 4. Protokoll zur Ausführung durch den KI-Agenten

Wenn der Benutzer dich auffordert, diesen Skill anzuwenden (z. B. *"Nutze den UX/UI-Skill, um meine App zu prüfen"*), folge diesem exakten Ablauf:

1. **Bestätige den Skill-Ladevorgang:** Zeige dem Benutzer, dass du dieses Dokument (`ux_ui_designer_skill.md`) verstanden hast.
2. **App starten:** Schlage das Starten des FastAPI-Backends vor (falls noch nicht aktiv).
3. **Browser-Audit starten:** Starte einen Browser-Subagenten, der die wichtigsten App-Screenshots sammelt.
4. **Audit-Report schreiben:** Erstelle das Dokument `ux_ui_audit_report.md` im `artifacts`-Verzeichnis mit allen Funden und Diffs.
5. **Gemeinsame Abstimmung:** Bitte den Benutzer um Feedback zu den vorgeschlagenen Design-Änderungen, bevor du den Code modifizierst.
