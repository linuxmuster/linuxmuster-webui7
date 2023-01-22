import lxml.etree as etree


def xml_propfind_response(r):
    valid_properties = {
        'getlastmodified',
        'quota-used-bytes',
        'quota-available-bytes',
        'getetag',
        'getcontentlength',
        'getcontenttype',
        'displayname',
    }

    root = etree.Element("{DAV:}multistatus", nsmap={"d": "DAV:"})

    for path, details in r.items():
        response = etree.SubElement(root, "{DAV:}response")
        href = etree.SubElement(response, "{DAV:}href")
        href.text = path
        propstat_200 = etree.SubElement(response, "{DAV:}propstat")
        propstat_404 = etree.SubElement(response, "{DAV:}propstat")
        prop_200 = etree.SubElement(propstat_200, "{DAV:}prop")
        prop_404 = etree.SubElement(propstat_404, "{DAV:}prop")
        status_200 = etree.SubElement(propstat_200, "{DAV:}status")
        status_404 = etree.SubElement(propstat_404, "{DAV:}status")
        status_200.text = "HTTP/1.1 200 OK"
        status_404.text = "HTTP/1.1 404 Not Found"

        for prop in valid_properties:
            value = details.get(prop, None)
            if value is None:
                etree.SubElement(prop_404, f"{{DAV:}}{prop}")
            else:
                prop = etree.SubElement(prop_200, f"{{DAV:}}{prop}")
                prop.text = value

        isdir = etree.SubElement(prop_200, f"{{DAV:}}resourcetype")
        if details['isDir']:
            etree.SubElement(isdir, f"{{DAV:}}collection")


    return etree.tostring(root).decode()