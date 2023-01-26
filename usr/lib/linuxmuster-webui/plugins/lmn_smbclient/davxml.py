import lxml.etree as etree

class WebdavXMLResponse:
    valid_properties = {
        # 'resourcetype', # --> collection or not
        'getlastmodified',
        'quota-used-bytes',
        'quota-available-bytes',
        'getetag',
        'getcontentlength',
        'getcontenttype',
        'displayname',
        'creationdate',
    }
    # Missing:
    # - getcontentlanguage
    # - lockdiscovery
    # - supportedlock

    def __init__(self):
        pass

    def make_propfind_response(self, items):
        xml_root = etree.Element("{DAV:}multistatus", nsmap={"d": "DAV:"})
        for href,properties in items.items():
            xml_response = etree.SubElement(xml_root, "{DAV:}response")
            xml_href = etree.SubElement(xml_response, "{DAV:}href")
            xml_href.text = href
            self._make_item_propstat(xml_response, properties)

        return etree.tostring(xml_root).decode()

    def _make_item_propstat(self, xml_response, properties):
        propstat_200 = etree.SubElement(xml_response, "{DAV:}propstat")
        propstat_404 = etree.SubElement(xml_response, "{DAV:}propstat")

        prop_200 = etree.SubElement(propstat_200, "{DAV:}prop")
        prop_404 = etree.SubElement(propstat_404, "{DAV:}prop")

        status_200 = etree.SubElement(propstat_200, "{DAV:}status")
        status_404 = etree.SubElement(propstat_404, "{DAV:}status")

        status_200.text = "HTTP/1.1 200 OK"
        status_404.text = "HTTP/1.1 404 Not Found"

        # TODO: replace valid_properties with requested prop
        for prop in self.valid_properties:
            value = properties.get(prop, None)
            if value is None:
                etree.SubElement(prop_404, f"{{DAV:}}{prop}")
            else:
                prop = etree.SubElement(prop_200, f"{{DAV:}}{prop}")
                prop.text = value

        isdir = etree.SubElement(prop_200, f"{{DAV:}}resourcetype")
        if properties['isDir']:
            etree.SubElement(isdir, f"{{DAV:}}collection")