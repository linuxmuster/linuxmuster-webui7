"""
Tools to handle files, directories and uploads.
"""

import os
from urllib.parse import quote, unquote
import locale
import gevent
import smbclient
from smbprotocol.exceptions import SMBOSError, NotFound, SMBAuthenticationError, InvalidParameter
from spnego.exceptions import BadMechanismError
from jadi import component
import xml.etree.ElementTree as ElementTree

from aj.api.http import url, get, post, mkcol, options, copy, move, put, propfind, delete, HttpPlugin
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

    @get(r'/webdav/(?P<path>.*)')
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
                if smbclient.path.isfile(smb_path) or smbclient.path.isdir(smb_path):
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
            if 'STATUS_ACCESS_DENIED' in e.strerror:
                http_context.respond_forbidden()
            else:
                http_context.respond_not_found()
            return ''


    @delete(r'/webdav/(?P<path>.*)')
    @endpoint()
    def handle_api_webdav_delete(self, http_context, path=''):

        path = self._convert_path(path).replace('/', '\\')
        path = f'{self.context.schoolmgr.schoolShare}{path}'

        try:
            if smbclient._os.SMBDirEntry.from_path(path).is_dir():
                smbclient.rmdir(path)
            else:
                smbclient.unlink(path)
            http_context.respond('204 No Content')
        except (ValueError, SMBOSError, NotFound) as e:
            if 'STATUS_ACCESS_DENIED' in e.strerror:
                http_context.respond_forbidden()
            else:
                http_context.respond_not_found()
        except InvalidParameter as e:
            http_context.respond_server_error()

        return ''

    @options(r'/webdav/(?P<path>.*)')
    @endpoint(api=True, auth=False)
    def handle_api_webdav_options(self, http_context, path=''):
        http_context.add_header("Allow", "OPTIONS, GET, HEAD, PUT, DELETE, COPY, MOVE")
        http_context.add_header("Allow", "MKCOL, PROPFIND")
        http_context.add_header("DAV", "1, 3")
        return ''

    @propfind(r'/webdav/(?P<path>.*)')
    @endpoint()
    def handle_api_webdav_propfind(self, http_context, path=''):
        user = self.context.identity
        profil = AuthenticationService.get(self.context).get_provider().get_profile(user)
        user_context = {
            'user': user,
            'role': profil['sophomorixRole'],
            'adminclass': profil['sophomorixAdminClass'],
            'home': profil['homeDirectory'],
        }

        baseUrl = "/webdav/"

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
            shares = self.context.schoolmgr.get_shares(user_context)
            for share in shares:
                item = smbclient._os.SMBDirEntry.from_path(share['path'])

                item_path = share['path'].replace(self.context.schoolmgr.schoolShare, '').replace('\\', '/') # TODO
                if share['name'] == "Home":
                    item_path = item_path.rsplit('/', 1)[0]

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

            except (BadMechanismError, SMBAuthenticationError, InvalidParameter) as e:
                 http_context.respond_server_error()
                 return ''
            except SMBOSError as e:
                if 'STATUS_ACCESS_DENIED' in e.strerror:
                    http_context.respond_forbidden()
                else:
                    http_context.respond_not_found()
                return ''

        http_context.respond('207 Multi-Status')
        http_context.add_header('Content-Type', 'application/xml; charset="utf-8"')

        return response.make_propfind_response(items)

    @mkcol(r'/webdav/(?P<path>.*)')
    @endpoint()
    def handle_api_dav_create_directory(self, http_context, path=''):
        if '..' in path:
            return http_context.respond_forbidden()

        path = self._convert_path(path).replace('/', '\\')
        try:
            smbclient.makedirs(f'{self.context.schoolmgr.schoolShare}{path}')
            http_context.respond("201 Created")
        except (ValueError, SMBOSError, NotFound) as e:
            if 'STATUS_ACCESS_DENIED' in e.strerror:
                http_context.respond_forbidden()
            else:
                http_context.respond_not_found()
        except InvalidParameter as e:
            http_context.respond_server_error()

        return ''

    @move(r'/webdav/(?P<path>.*)')
    @endpoint()
    def handle_api_dav_move(self, http_context, path=''):
        if '..' in path:
            return http_context.respond_forbidden()
        try:
            src = self._convert_path(path).replace('/', '\\')
            src = f'{self.context.schoolmgr.schoolShare}{src}'

            env = http_context.env
            dst = env.get('HTTP_DESTINATION', None)
            host = f"{env['wsgi.url_scheme']}://{env['HTTP_HOST']}/webdav/"
            dst = dst.replace(host, '')  # Delete host domain
            dst = dst.replace('/', '\\')
            dst = f'{self.context.schoolmgr.schoolShare}{dst}'

            overwrite = http_context.env.get('Overwrite', None) != 'F'

            if smbclient._os.SMBDirEntry.from_path(src).is_dir():
                if not smbclient.path.isdir(dst):
                    smbclient.rename(src, dst)
                    http_context.respond('201 Created')
                elif smbclient.path.isdir(dst) and overwrite:
                    smbclient.rename(src, dst)
                    http_context.respond('204 No Content')
                elif smbclient.path.isdir(dst):
                    http_context.respond('412 Precondition Failed')
            else:
                if not smbclient.path.isfile(dst):
                    smbclient.rename(src, dst)
                    http_context.respond('201 Created')
                elif smbclient.path.isfile(dst) and overwrite:
                    smbclient.rename(src, dst)
                    http_context.respond('204 No Content')
                elif smbclient.path.isfile(dst):
                    http_context.respond('412 Precondition Failed')
        except (ValueError, SMBOSError, NotFound) as e:
            if 'STATUS_ACCESS_DENIED' in e.strerror:
                http_context.respond_forbidden()
            else:
                http_context.respond_not_found()
        except InvalidParameter as e:
            http_context.respond_server_error()

        return ''

    @copy(r'/webdav/(?P<path>.*)')
    @endpoint()
    def handle_api_dav_copy(self, http_context, path=''):
        if '..' in path:
            return http_context.respond_forbidden()
        try:
            src = self._convert_path(path).replace('/', '\\')
            src = f'{self.context.schoolmgr.schoolShare}{src}'
            env = http_context.env
            dst = env.get('HTTP_DESTINATION', None)
            host = f"{env['wsgi.url_scheme']}://{env['HTTP_HOST']}/webdav/"

            dst = dst.replace(host, '')  # Delete host domain
            dst = dst.replace('/', '\\')
            dst = f'{self.context.schoolmgr.schoolShare}{dst}'

            overwrite = http_context.env.get('Overwrite', None) != 'F'

            if smbclient._os.SMBDirEntry.from_path(src).is_dir():
                # First pass : create directory tree
                for item in smbclient.walk(src):
                    # item like (SMBPATH, [List of subdir], [List of files])
                    smbpath = item[0]
                    if smbclient.path.isdir(smbpath):
                        smbpath = smbpath.replace(src, dst)
                        smbclient.mkdir(smbpath)

                # Second pass : copy all files
                for item in smbclient.walk(src):
                    smbpath = item[0]
                    for file in item[2]:
                        smbpathsrc = f"{smbpath}\\{file}"
                        smbpathdst = smbpathsrc.replace(src, dst)
                        smbclient.copyfile(smbpathsrc, smbpathdst)
            else:
                if not smbclient.path.isfile(dst):
                    smbclient.copyfile(src, dst)
                    http_context.respond('201 Created')
                elif smbclient.path.isfile(dst) and overwrite:
                    smbclient.copyfile(src, dst)
                    http_context.respond('204 No Content')
                elif smbclient.path.isfile(dst):
                    http_context.respond('412 Precondition Failed')
        except (ValueError, SMBOSError, NotFound) as e:
            if 'STATUS_ACCESS_DENIED' in e.strerror:
                http_context.respond_forbidden()
            else:
                http_context.respond_not_found()
        except InvalidParameter as e:
            http_context.respond_server_error()

        return ''

    @put(r'/webdav/(?P<path>.*)')
    @endpoint()
    def handle_api_dav_put(self, http_context, path=''):
        if '..' in path:
            return http_context.respond_forbidden()
        try:
            dst = self._convert_path(path).replace('/', '\\')
            dst = f'{self.context.schoolmgr.schoolShare}{dst}'
            if not smbclient.path.isfile(dst):
                with smbclient.open_file(dst, mode='wb') as f:
                    f.write(http_context.body)
                http_context.respond_ok()
        except (ValueError, SMBOSError, NotFound) as e:
            if 'STATUS_ACCESS_DENIED' in e.strerror:
                http_context.respond_forbidden()
            else:
                http_context.respond_not_found()
        except InvalidParameter as e:
            http_context.respond_server_error()

        return ''