from os import path
from pykml import parser
from lxml import etree
import requests
from pykml.factory import KML_ElementMaker as KML
from lxml.html import fromstring

HREF = "<a href="
HREF_END = "\">"


def count_page_urls(old_placemark):
    description = old_placemark.description.text
    return description.count(HREF)


def get_page_url(old_placemark):
    description = old_placemark.description.text
    if HREF in description:
        return description[description.find(HREF) + len(HREF) + 1:description.find(HREF_END)]
    return None


def generate_name(old_placemark):
    if count_page_urls(old_placemark) > 1:
        return "" + str(count_page_urls(old_placemark)) + " via ferratas"

    url = get_page_url(old_placemark)
    if url:
        headers = {'User-Agent': 'Mozilla/5'}
        print(url)
        r = requests.get(url, headers=headers)
        tree = fromstring(r.content)
        title = tree.findtext('.//title')
        print(title)
        title_trimmed = title.replace("ViaFerrata-FR.net: ", "")
        return title_trimmed[:title_trimmed.find(" /")]
    else:
        return old_placemark.name.text


def generate_description(old_placemark):
    return "dupa"


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
