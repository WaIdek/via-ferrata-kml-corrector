from os import path

from pykml import parser
from lxml import etree
from lxml import html
import requests
from pykml.factory import KML_ElementMaker as KML
from pykml.factory import GX_ElementMaker as GX
from pykml.factory import nsmap
from pykml.parser import Schema


def get_page_url(old_placemark):
    description = old_placemark.description
    if "<a href=" in description:
        return description[description.find("<a href=")+8:description.find("\">")]
    return None


def generate_name(old_placemark):
    url = get_page_url(old_placemark)
    if url:
        page = requests.get(url)
        tree = html.fromstring(page.content)
        title = tree.head.title
        title_trimmed = title.replace("ViaFerrata-FR.net: ","")
        return title_trimmed[:title_trimmed.find("/")]
    else:
        return old_placemark.name


def generate_description(old_placemark):
    pass


def generate_placemark(old_placemark):
    return KML.Placemark(
        KML.name(generate_name(old_placemark)),
        KML.description(generate_description(old_placemark)),
        KML.visibility(1),
        KML.Point(KML.coordinates(old_placemark.Point.coordinates.text))
    )


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

out_doc = KML.kml(
    KML.Document(
        KML.name('French Via Ferratas')
    )
)

kml_file = path.join('via-ferrata-france.kml')

with open(kml_file) as f:
    doc = parser.parse(f)
    root = doc.getroot()
    for placemark in root.Document.Placemark:
        out_doc.Document.append(generate_placemark(placemark))

outfile = open(__file__.rstrip('.py') + '.kml', 'wb')
outfile.write(etree.tostring(out_doc, pretty_print=True))
outfile.close()
