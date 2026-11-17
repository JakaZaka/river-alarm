import json, os, sys, urllib.request
import xml.etree.ElementTree as ET

URL = "http://www.arso.gov.si/xml/vode/hidro_podatki_zadnji.xml"
SIFRA = "4570"
THRESHOLD = float(os.environ.get("THRESHOLD", "230"))
TOPIC = os.environ["NTFY_TOPIC"]

def notify(title, message):
    body = json.dumps({"topic": TOPIC, "title": title, "message": message,
                       "priority": 5, "tags": ["warning"]}).encode()
    req = urllib.request.Request("https://ntfy.sh", data=body,
                                 headers={"Content-Type": "application/json"})
    urllib.request.urlopen(req, timeout=30)

data = urllib.request.urlopen(URL, timeout=30).read()
root = ET.fromstring(data)
st = next((e for e in root.iter() if e.get("sifra") == SIFRA), None)
if st is None:
    sys.exit(f"Postaja {SIFRA} ni najdena")
el = st.find("vodostaj")
if el is None or not (el.text or "").strip():
    print(ET.tostring(st, encoding="unicode"))
    sys.exit("Polje vodostaj ni najdeno; glej strukturo zgoraj")

level = float(el.text.strip().replace(",", "."))
print(f"Vodostaj: {level} cm (prag {THRESHOLD})")
if level > THRESHOLD:
    notify("Pšata Topole visoka!", f"Vodostaj {level:.0f} cm (prag {THRESHOLD:.0f} cm)")
