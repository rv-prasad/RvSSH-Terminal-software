import xml.etree.ElementTree as ET

def import_securecrt_xml(path):
    tree = ET.parse(path)
    root = tree.getroot()

    return {
        "name": root.find(".//SessionName").text,
        "host": root.find(".//HostName").text,
        "port": int(root.find(".//Port").text),
        "username": root.find(".//Username").text,
        "auth": "password"
    }