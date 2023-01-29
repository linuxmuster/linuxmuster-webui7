"""
Tools to handle files, directories and uploads.
"""

import os
from urllib.parse import quote, unquote
import locale
import gevent
import logging
import smbclient
from smbprotocol.exceptions import SMBOSError, NotFound, SMBAuthenticationError, InvalidParameter
from spnego.exceptions import BadMechanismError
from jadi import component
import xml.etree.ElementTree as ElementTree

from aj.api.http import url, get, post, mkcol, options, copy, move, propfind, delete, HttpPlugin
from aj.api.endpoint import endpoint, EndpointError, EndpointReturn
from aj.auth import authorize, AuthenticationService
from aj.plugins.lmn_common.mimetypes import content_mimetypes
from aj.plugins.lmn_smbclient.davxml import WebdavXMLResponse


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    def _convert_path(self, path):
        # In gevent, headers are decoded with latin-1
        # Dirty fix for it
        return path.encode('latin-1').decode('utf-8')

    @get(r'/api/lmn/webdav/(?P<path>.*)')
    @endpoint(page=True)
    def handle_api_webdav_get(self, http_context, path=''):
        if '..' in path:
            return http_context.respond_forbidden()

        path = self._convert_path(unquote(path))
        name = path.split('/')[-1]
        ext = os.path.splitext(name)[1]

        smb_path = path.replace('/', '\\')
        smb_path = f'{self.context.schoolmgr.schoolShare}{smb_path}'

        try:
            smbclient.path.isfile(smb_path)
            # Head request to handle 404
            if http_context.method == 'HEAD':
                if smbclient.path.isfile(smb_path):
                    http_context.respond_ok()
                    return ''
                else:
                    http_context.respond_not_found()
                    return ''
        except (ValueError, SMBOSError, NotFound):
            http_context.respond_not_found()
            return ''

        if ext in content_mimetypes:
            http_context.add_header('Content-Type', content_mimetypes[ext])
        else:
            http_context.add_header('Content-Type', 'application/octet-stream')

        http_range = http_context.env.get('HTTP_RANGE', None)
        http_context.add_header('Accept-Ranges', 'bytes')

        try:
            if http_range and http_range.startswith('bytes'):
                rsize = smbclient.stat(smb_path).st_size
                range_from, range_to = http_range.split('=')[1].split('-')
                range_from = int(range_from) if range_from else 0
                range_to = int(range_to) if range_to else (rsize - 1)
            else:
                range_from = 0
                range_to = 999999999

            if range_from:
                http_context.add_header('Content-Length', str(range_to - range_from + 1))
                http_context.add_header('Content-Range',
                                f'bytes {range_from:d}-{range_to:d}/{rsize}')
                http_context.respond('206 Partial Content')
            else:
                http_context.respond_ok()

            http_context.add_header('Content-Disposition', (f'attachment; filename={name}'))

            fd = smbclient._os.open_file(smb_path, 'rb')
            fd.seek(range_from or 0, smbclient._os.os.SEEK_SET)
            bufsize = 100 * 1024
            read = range_from
            buf = 1
            while buf:
                buf = fd.read(bufsize)
                gevent.sleep(0)
                if read + len(buf) > range_to:
                    buf = buf[:range_to + 1 - read]
                yield buf
                read += len(buf)
                if read >= range_to:
                    break
            fd.close()
        except (ValueError, SMBOSError, NotFound) as e:
            logging.error(e)
            http_context.respond_not_found()
            return ''


    @delete(r'/api/lmn/webdav/(?P<path>.*)')
    @endpoint(api=True)
    def handle_api_webdav_delete(self, http_context, path=''):

        path = self._convert_path(path).replace('/', '\\')

        try:
            smbclient.unlink(f'{self.context.schoolmgr.schoolShare}{path}')
            http_context.respond('204 No Content')
            return ''
        except (ValueError, SMBOSError, NotFound) as e:
            http_context.respond_not_found()
            return ''
        except InvalidParameter as e:
            #raise EndpointError(f'Problem with path {path} : {e}')
            http_context.respond_server_error()
            return ''

    @options(r'/api/lmn/webdav/(?P<path>.*)')
    @endpoint(api=True, auth=False)
    def handle_api_webdav_options(self, http_context, path=''):
        http_context.add_header("Allow", "OPTIONS, GET, HEAD, POST, DELETE, COPY, MOVE")
        http_context.add_header("Allow", "MKCOL, PROPFIND")
        http_context.add_header("DAV", "1, 3")
        return ''

    @propfind(r'/api/lmn/webdav/(?P<path>.*)')
    @endpoint()
    def handle_api_webdav_propfind(self, http_context, path=''):
        user = self.context.identity
        profil = AuthenticationService.get(self.context).get_provider().get_profile(user)
        role = profil['sophomorixRole']
        adminclass = profil['sophomorixAdminClass']

        baseUrl = "/api/lmn/webdav/"

        # READ XML body for requested properties
        if b'<?xml' in http_context.body:
            tree = ElementTree.fromstring(http_context.body)
            allprop = tree.findall('.//{DAV:}allprop')
            if allprop:
                requested_properties = None
            else:
                requested_properties = {p.tag for p in tree.findall('.//{DAV:}prop/*')}
                requested_properties = {r.replace('{DAV:}', '') for r in requested_properties}

        items = {}
        locale.setlocale(locale.LC_ALL, 'C')
        response = WebdavXMLResponse(requested_properties)

        if not path:
            # / is asked, must give the list of shares
            shares = self.context.schoolmgr.get_shares(user, role, adminclass)
            for share in shares:
                item = smbclient._os.SMBDirEntry.from_path(share['path'])

                item_path = share['path'].replace(self.context.schoolmgr.schoolShare, '').replace('\\', '/') # TODO
                if share['name'] == "Home":
                    item_path = item_path.split('/')[0]

                href = quote(f'{baseUrl}{item_path}/', encoding='utf-8')
                items[href] = response.convert_samba_entry_properties(item)
                items[href]['displayname'] = share['name']
        else:
            url_path = self._convert_path(path).replace('/', '\\')
            smb_path = f"{self.context.schoolmgr.schoolShare}{url_path}"
            smb_entity = smbclient._os.SMBDirEntry.from_path(smb_path)

            try:
                if smb_entity.is_dir():
                    # Listing a directory
                    for item in smbclient.scandir(smb_path):
                        item_path = os.path.join(path, item.name).replace('\\', '/') # TODO
                        href = quote(f'{baseUrl}{item_path}', encoding='utf-8')
                        items[href] = response.convert_samba_entry_properties(item)
                else:
                    # Request only the properties of one single file
                    item = smb_entity
                    item_path = path.replace('\\', '/') # TODO
                    href = quote(f'{baseUrl}{item_path}', encoding='utf-8')
                    items[href] = response.convert_samba_entry_properties(item)

            except (BadMechanismError, SMBAuthenticationError) as e:
                 raise EndpointError(f"There's a problem with the kerberos authentication : {e}")
            except InvalidParameter as e:
                 raise EndpointError("This server does not support this feature actually, but it will come soon!")
            except SMBOSError as e:
                http_context.respond_not_found()
                return ''

        http_context.respond('207 Multi-Status')
        http_context.add_header('Content-Type', 'application/xml; charset="utf-8"')

        return response.make_propfind_response(items)

    @mkcol(r'/api/lmn/webdav/(?P<path>.*)')
    @endpoint(api=True)
    def handle_api_dav_create_directory(self, http_context, path=''):
        if '..' in path:
            return http_context.respond_forbidden()

        path = self._convert_path(path).replace('/', '\\')
        try:
            smbclient.makedirs(f'{self.context.schoolmgr.schoolShare}{path}')
        except (ValueError, SMBOSError, NotFound) as e:
            raise EndpointError(e)
        except InvalidParameter as e:
            raise EndpointError(f'Problem with path {path} : {e}')
        return ''