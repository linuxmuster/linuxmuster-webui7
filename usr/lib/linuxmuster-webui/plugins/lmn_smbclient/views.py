"""
Tools to handle files, directories and uploads.
"""

import os
import re
import smbclient
from smbprotocol.exceptions import SMBOSError, NotFound, SMBAuthenticationError, InvalidParameter
from spnego.exceptions import BadMechanismError
from jadi import component

from aj.api.http import url, get, post, HttpPlugin
from aj.api.endpoint import endpoint, EndpointError, EndpointReturn
from aj.auth import authorize, AuthenticationService
from aj.plugins.lmn_common.mimetypes import content_mimetypes


# TODO
# - Better error management (directory not empty, errors in promise list, ... )
# - Test encoding Windows
# - symlink ?
# - download selected resources as zip
# - Method DELETE ?

@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @get(r'/api/lmn/smbclient/shares/(?P<user>.+)')
    @endpoint(api=True)
    def handle_api_smb_shares(self, http_context, user=None):
        """
        Return a list of hard-coded shares per role.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: All items with informations
        :rtype: dict
        """

        if user is None:
            user = self.context.identity

        profil = AuthenticationService.get(self.context).get_provider().get_profile(user)
        role = profil['sophomorixRole']
        adminclass = profil['sophomorixAdminClass']
        return self.context.schoolmgr.get_shares(user, role, adminclass)

    @post(r'/api/lmn/smbclient/list')
    @endpoint(api=True)
    def handle_api_smb_list(self, http_context):
        """
        Return a list of objects (files, directories, ...) in a specific samba share.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: All items with informations
        :rtype: dict
        """

        def SMB2UnixPath(path):
            path = path.replace('\\', '/')

            if 'linuxmuster-global' in path:
                root = '/srv/samba/schools/global'
            else:
                root = f'/srv/samba/schools/{self.context.schoolmgr.school}'

            return os.path.join(root, *list(filter(None, path.split('/')))[2:])

        path = http_context.json_body()['path']

        try:
            items = []
            for item in smbclient.scandir(path):
                item_path = os.path.join(path, item.name) # TODO

                data = {
                    'name': item.name,
                    'path': item_path,
                    'unixPath': SMB2UnixPath(item_path),
                    'isDir': item.is_dir(),
                    'isFile': item.is_file(),
                    'isLink': item.is_symlink(),
                }

                try:
                    stat = item.stat()
                    data.update({
                        'mode': stat.st_mode,
                        'mtime': stat.st_mtime,
                        'uid': stat.st_uid,
                        'gid': stat.st_gid,
                        'size': stat.st_size,
                    })
                except (ValueError, SMBOSError, NotFound) as e:
                    data['accessError'] = str(e)
                    # if e.errno == errno.ENOENT and os.path.islink(item_path):
                    #     data['brokenLink'] = True

                items.append(data)
        except (BadMechanismError, SMBAuthenticationError) as e:
            raise EndpointError(f"There's a problem with the kerberos authentication : {e}")
        except InvalidParameter as e:
            raise EndpointError("This server does not support this feature actually, but it will come soon!")
        return {
            'parent': '', # TODO
            'items': items
        }

    @post(r'/api/lmn/smbclient/directory')
    @endpoint(api=True)
    def handle_api_smb_create_directory(self, http_context):
        """
        Create empty directory on specified path.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :param path: Path of directory
        :type path: string
        """

        path = http_context.json_body()['path']

        try:
            smbclient.makedirs(path)
        except (ValueError, SMBOSError, NotFound) as e:
            raise EndpointError(e)
        except InvalidParameter as e:
            raise EndpointError(f'Problem with path {path} : {e}')

    @post(r'/api/lmn/smbclient/file')
    @endpoint(api=True)
    def handle_api_smb_create_file(self, http_context):
        """
        Create empty file on specified path.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :param path: Path of directory
        :type path: string
        """

        path = http_context.json_body()['path']

        try:
            with smbclient.open_file(path, 'w') as towrite:
                pass
        except (ValueError, SMBOSError, NotFound) as e:
            raise EndpointError(e)
        except InvalidParameter as e:
            raise EndpointError(f'Problem with path {path} : {e}')

    @post(r'/api/lmn/smbclient/move')
    @endpoint(api=True)
    def handle_api_smb_move(self, http_context):
        """
        Move src to dst, work with files and directories.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :param path: Path of directory
        :type path: string
        """

        src = http_context.json_body()['src']
        dst = http_context.json_body()['dst']

        try:
            smbclient.rename(src, dst)
        except (ValueError, SMBOSError, NotFound) as e:
            raise EndpointError(e)

    @post(r'/api/lmn/smbclient/copy')
    @endpoint(api=True)
    def handle_api_smb_copy(self, http_context):
        """
        Make a copy of file src to dst.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :param path: Path of directory
        :type path: string
        """

        src = http_context.json_body()['src']
        dst = http_context.json_body()['dst']

        try:
            smbclient.copyfile(src, dst)
        except (ValueError, SMBOSError, NotFound) as e:
            raise EndpointError(e)

    @post(r'/api/lmn/smbclient/rmdir') # TODO : bad method, should be delete
    @endpoint(api=True)
    def handle_api_smb_rmdir(self, http_context):
        """
        Delete an empty directory. Throw an SMBOSError if the directory is
        not empty.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :param path: Path of directory
        :type path: string
        """

        path = http_context.json_body()['path']

        try:
            smbclient.rmdir(path)
        except (ValueError, SMBOSError, NotFound) as e:
            raise EndpointError(e)

    @post(r'/api/lmn/smbclient/unlink') # TODO : bad method, should be delete
    @endpoint(api=True)
    def handle_api_smb_unlink(self, http_context):
        """
        Delete a file.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :param path: Path of directory
        :type path: string
        """

        path = http_context.json_body()['path']

        try:
            smbclient.unlink(path)
        except (ValueError, SMBOSError, NotFound) as e:
            raise EndpointError(e)

    @get(r'/api/lmn/smbclient/stat/(?P<path>.+)')
    @endpoint(api=True)
    def handle_api_smb_stat(self, http_context, path=None):
        """
        Get all informations from a specific path.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :param path: Path of file/directory
        :type path: string
        :return: POSIX permissions, size, type, ...
        :rtype: dict
        """

        smb_file = smbclient._os.SMBDirEntry.from_path(path)
        data = {
                    'name': smb_file.name,
                    'path': path, # TODO
                    'isDir': smb_file.is_dir(),
                    'isFile': smb_file.is_file(),
                    'isLink': smb_file.is_symlink(),
                }
        # unix permissions ?

        try:
            stat = smb_file.stat()
            data.update({
                'mode': stat.st_mode,
                'mtime': stat.st_mtime,
                'uid': stat.st_uid,
                'gid': stat.st_gid,
                'size': stat.st_size,
            })
        except (ValueError, SMBOSError, NotFound) as e:
            data['accessError'] = str(e)

        return data

    @get(r'/api/lmn/smbclient/upload')
    @endpoint(page=True)
    def handle_api_smb_get_upload_chunk(self, http_context):
        """
        Write a chunk part of an upload in HOME/.upload//upload*/<index>.
        If method get is called, verify if the chunk part is present.
        Method GET.

        :param http_context: HttpContext
        :type http_context: HttpContext
        """

        user = self.context.identity
        profil = AuthenticationService.get(self.context).get_provider().get_profile(user)
        role = profil['sophomorixRole']
        adminclass = profil['sophomorixAdminClass']
        home = self.context.schoolmgr.get_homepath(user, role, adminclass)
        upload_dir = f'{home}\\.upload'

        if not smbclient.path.exists(upload_dir):
            smbclient.mkdir(upload_dir)

        id = http_context.query['flowIdentifier']
        chunk_index = http_context.query['flowChunkNumber']
        chunk_dir = f'{upload_dir}\\upload-{id}'

        try:
            smbclient.mkdir(chunk_dir)
        except Exception as e:
            pass

        chunk_path = f'{chunk_dir}\\{chunk_index}'

        if smbclient.path.exists(chunk_path):
            http_context.respond('200 OK')
        else:
            http_context.respond('204 No Content')
        return ''

    @post(r'/api/lmn/smbclient/upload')
    @endpoint(page=True)
    def handle_api_smb_post_upload_chunk(self, http_context):
        """
        Write a chunk part of an upload in HOME/.upload//upload*/<index>.

        :param http_context: HttpContext
        :type http_context: HttpContext
        """

        user = self.context.identity
        profil = AuthenticationService.get(self.context).get_provider().get_profile(user)
        role = profil['sophomorixRole']
        adminclass = profil['sophomorixAdminClass']
        home = self.context.schoolmgr.get_homepath(user, role, adminclass)
        upload_dir = f'{home}\\.upload'

        if not smbclient.path.exists(upload_dir):
            smbclient.mkdir(upload_dir)

        id = http_context.query['flowIdentifier']
        chunk_index = http_context.query['flowChunkNumber']
        chunk_dir = f'{upload_dir}\\upload-{id}'

        try:
            smbclient.mkdir(chunk_dir)
        except Exception as e:
            pass

        chunk_path = f'{chunk_dir}\\{chunk_index}'

        with smbclient.open_file(chunk_path, mode='wb') as f:
            f.write(http_context.query['file'])
        http_context.respond('200 OK')
        return ''

    @post(r'/api/lmn/smbclient/finish-upload')
    # @authorize('smbclient:write')
    @endpoint(api=True)
    def handle_api_smb_finish_upload(self, http_context):
        """
        Build all chunk parts from an uploaded file together and return it.
        Clean the tmp directory.
        Method POST.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Path of files
        :rtype: list of string
        """

        # files should be a list of dict
        files = http_context.json_body()
        targets = []

        user = self.context.identity
        profil = AuthenticationService.get(self.context).get_provider().get_profile(user)
        role = profil['sophomorixRole']
        adminclass = profil['sophomorixAdminClass']
        home = self.context.schoolmgr.get_homepath(user, role, adminclass)
        upload_dir = f'{home}/.upload'

        for file in files:
            name = file['name'].replace('/', '')
            path = file['path']
            id = file['id']
            chunk_dir = f'{upload_dir}/upload-{id}'

            target = f'{path}/{name}'

            try:
                # Avoid overwriting existing file
                while smbclient.path.isfile(target):
                    try:
                        last, ext = list(filter(None, name.split('.')))[-2:]
                    except (IndexError, ValueError):
                        last = name.split('.')[-1]
                        ext = ''
                    # Test if previously numbered
                    count = re.match('.* \((\d+)\)$', last)

                    if ext:
                        ext = f'.{ext}'

                    if count:
                        new_count = int(count.group(1)) + 1
                        name = re.sub(f' \(\d+\){ext}$', f' ({new_count}){ext}', name)
                    else:
                        name = re.sub(f'{ext}$', f' (1){ext}', name)

                    target = f'{path}/{name}'
            except SMBOSError:
                # That's ok we can write a new file
                pass

            with smbclient.open_file(target, mode='wb') as f:
                for i in range(len(smbclient.listdir(chunk_dir))):
                    chunk_file = f'{chunk_dir}/{str(i+1)}'
                    with smbclient.open_file(chunk_file, mode='rb') as chunk:
                        f.write(chunk.read())
                    smbclient.remove(chunk_file)

            smbclient.rmdir(chunk_dir)

            targets.append({
                'name': name,
                'path': target,
                'unixPath': '',
                'isDir': False,
                'isFile': True,
                'isLink': False,
            })
        return targets

    @url(r'/api/lmn/smbclient/download') # TODO : wait until Ajenti supports head for get requests
    @endpoint(page=True)
    def handle_smb_download(self, http_context):
        path = http_context.query.get('path', None)

        if '..' in path:
            return http_context.respond_forbidden()

        try:
            smbclient.path.isfile(path)
            # Head request to handle 404 in Angular
            if http_context.method == 'HEAD':
                http_context.respond('200 OK')
                return ''
        except (ValueError, SMBOSError, NotFound):
            http_context.respond_not_found()
            return

        name = path.split('/')[-1]
        ext = os.path.splitext(name)[1]

        if ext in content_mimetypes:
            http_context.add_header('Content-Type', content_mimetypes[ext])
        else:
            http_context.add_header('Content-Type', 'application/octet-stream')

        try:
            content = smbclient.open_file(path, 'rb').read()
        except (ValueError, SMBOSError, NotFound):
            http_context.respond_not_found()
            return

        http_context.add_header('Content-Disposition', (f'attachment; filename={name}'))

        yield http_context.gzip(content)
