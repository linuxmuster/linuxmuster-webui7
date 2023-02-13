import hashlib
import os
import pytz
from dateutil.tz import tzlocal
import lxml.etree as etree
from datetime import datetime

from aj.plugins.lmn_common.mimetypes import content_mimetypes


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

    def __init__(self, requested_properties=None):
        if requested_properties is None:
            # Gives all properties
            self.requested_properties = self.valid_properties
        else:
            self.requested_properties = requested_properties.intersection(self.valid_properties)

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

        for prop in self.requested_properties:
            value = properties.get(prop, None)
            if value is None:
                etree.SubElement(prop_404, f"{{DAV:}}{prop}")
            else:
                prop = etree.SubElement(prop_200, f"{{DAV:}}{prop}")
                prop.text = value

        isdir = etree.SubElement(prop_200, f"{{DAV:}}resourcetype")
        if properties['isDir']:
            etree.SubElement(isdir, f"{{DAV:}}collection")

    def _make_gmt_time(self, timestamp):
        # Convert modified time to GMT
        local_time = datetime.fromtimestamp(timestamp, tz=tzlocal())
        gmt_time = local_time.astimezone(pytz.timezone("Etc/GMT"))
        return gmt_time.strftime("%a, %d %b %Y %H:%M:%S %Z")

    def convert_samba_entry_properties(self, item):
        stat = item.stat()

        raw_etag = f"{item.name}-{stat.st_size}-{stat.st_mtime}".encode()
        etag = hashlib.md5(raw_etag).hexdigest()

        ext = os.path.splitext(item.name)[1]
        content_type = "application/octet-stream"
        if ext in content_mimetypes:
            content_type = content_mimetypes[ext]

        return {
            'isDir': item.is_dir(),
            'getlastmodified': self._make_gmt_time(stat.st_mtime),
            'creationdate': self._make_gmt_time(stat.st_ctime),
            'getcontentlength': str(stat.st_size),
            'getcontenttype': None if item.is_dir() else content_type,
            'getetag': etag,
            'displayname': item.name,
        }
