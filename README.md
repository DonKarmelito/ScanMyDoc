# ScanMyDoc 📄

Inteligentny skaner dokumentów zbudowany w Streamlit. Wgraj zdjęcie kartki, przytnij perspektywę i pobierz gotowy PDF. Możesz też scalić kilka skanów w jeden plik.

## Funkcje

- **Kadrowanie automatyczne** — wykrywa kartę na zdjęciu i przycina perspektywę
- **Kadrowanie ręczne** — kliknij 4 rogi dokumentu na canvasie
- **Efekt skanera** — konwersja do czarno-białego z regulowanym kontrastem
- **Scalanie PDF** — połącz wiele skanów w jeden plik

## Struktura projektu

```
scanmydoc/
├── app.py              # UI i routing (Streamlit)
├── processing.py       # Logika przetwarzania obrazu (OpenCV)
├── pdf_utils.py        # Generowanie i scalanie PDF
├── canvas_utils.py     # Obsługa drawable canvas
├── styles.py           # Style CSS + paleta kolorów
├── requirements.txt
└── assets/
    ├── logo.png
    └── uplogo.png
```

## Instalacja lokalna

```bash
git clone https://github.com/TWOJ_LOGIN/scanmydoc.git
cd scanmydoc

python -m venv .venv
source .venv/bin/activate        # Linux/Mac
# lub: .venv\Scripts\activate    # Windows

pip install -r requirements.txt
streamlit run app.py
```

## Deploy na Streamlit Cloud

1. Wgraj repo na GitHub
2. Wejdź na [share.streamlit.io](https://share.streamlit.io)
3. Połącz repo → ustaw `app.py` jako entry point → Deploy

## Zmiana kolorów

Wszystkie kolory są w jednym miejscu — słownik `COLORS` w pliku `styles.py`:

```python
COLORS = {
    "bg":       "#12131a",
    "accent":   "#f5960a",   # główny kolor akcentu
    # ...
}
```

---
Powered by **KarmelCodeLab**
