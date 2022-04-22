"""
Tools to handle files, directories and uploads.
"""

import os
import smbclient
import logging
from smbprotocol.exceptions import SMBOSError
from jadi import component

from aj.api.http import url, HttpPlugin
from aj.api.endpoint import endpoint, EndpointError, EndpointReturn
from aj.auth import authorize, AuthenticationService
from aj.plugins.lmn_common.mimetypes import content_mimetypes

# TODO
# - HomeService
# - Handle end of ticket
# - Better error management (file already exists, directory not empty, ... )
# - Test encoding Windows
# - chmod
# - mknod
# - upload
# - read/write/create file
# - symlink ?
# - download selected resources as zip
# - Method DELETE ?

@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @url(r'/api/lmn/smbclient/list')
    # @authorize('smbclient:read')
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

        if http_context.method == 'POST':
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
                    except SMBOSError as e:
                        data['accessError'] = str(e)
                        # if e.errno == errno.ENOENT and os.path.islink(item_path):
                        #     data['brokenLink'] = True

                    items.append(data)
            except Exception as e: #spnego.exceptions.BadMechanismError:
                logging.error("%s", e)
                return {}
            return {
                'parent': '', # TODO
                'items': items
            }

    @url(r'/api/lmn/smbclient/create-directory')
    # @authorize('smbclient:write')
    @endpoint(api=True)
    def handle_api_smb_create_directory(self, http_context):
        """
        Create empty directory on specified path.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :param path: Path of directory
        :type path: string
        """

        if http_context.method == 'POST':
            path = http_context.json_body()['path']

            try:
                smbclient.makedirs(path)
            except (ValueError, SMBOSError) as e:
                raise EndpointError(e)

    @url(r'/api/lmn/smbclient/move')
    # @authorize('smbclient:write')
    @endpoint(api=True)
    def handle_api_smb_move(self, http_context):
        """
        Move src to dst, work with files and directories.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :param path: Path of directory
        :type path: string
        """

        if http_context.method == 'POST':
            src = http_context.json_body()['src']
            dst = http_context.json_body()['dst']

            try:
                smbclient.rename(src, dst)
            except (ValueError, SMBOSError) as e:
                raise EndpointError(e)

    @url(r'/api/lmn/smbclient/copy')
    # @authorize('smbclient:write')
    @endpoint(api=True)
    def handle_api_smb_copy(self, http_context):
        """
        Make a copy of file src to dst.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :param path: Path of directory
        :type path: string
        """

        if http_context.method == 'POST':
            src = http_context.json_body()['src']
            dst = http_context.json_body()['dst']

            try:
                smbclient.copyfile(src, dst)
            except (ValueError, SMBOSError) as e:
                raise EndpointError(e)

    @url(r'/api/lmn/smbclient/dir')
    # @authorize('smbclient:write')
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

        if http_context.method == 'POST':
            path = http_context.json_body()['path']

            try:
                smbclient.rmdir(path)
            except (ValueError, SMBOSError) as e:
                raise EndpointError(e)

    @url(r'/api/lmn/smbclient/file')
    # @authorize('smbclient:write')
    @endpoint(api=True)
    def handle_api_smb_unlink(self, http_context):
        """
        Delete a file.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :param path: Path of directory
        :type path: string
        """

        if http_context.method == 'POST':
            path = http_context.json_body()['path']

            try:
                smbclient.unlink(path)
            except (ValueError, SMBOSError) as e:
                raise EndpointError(e)

    @url(r'/api/lmn/smbclient/stat')
    # @authorize('smbclient:read')
    @endpoint(api=True)
    def handle_api_smb_stat(self, http_context):
        """
        Get all informations from a specific path.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :param path: Path of file/directory
        :type path: string
        :return: POSIX permissions, size, type, ...
        :rtype: dict
        """

        if http_context.method == 'POST':
            path = http_context.json_body()['path']
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
            except SMBOSError as e:
                data['accessError'] = str(e)

        return data

    @url(r'/api/lmn/smbclient/upload')
    # @authorize('smbclient:write')
    @endpoint(page=True)
    def handle_api_smb_upload_chunk(self, http_context):
        """
        Write a chunk part of an upload in HOME/.upload//upload*/<index>.
        If method get is called, verify if the chunk part is present.
        Method GET.

        :param http_context: HttpContext
        :type http_context: HttpContext
        """

        user = self.context.identity
        home = AuthenticationService.get(self.context).get_provider().get_profile(user)['homeDirectory']
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

        if http_context.method == 'GET':
            if smbclient.path.exists(chunk_path):
                http_context.respond('200 OK')
            else:
                http_context.respond('204 No Content')
        else:
            with smbclient.open_file(chunk_path, mode='wb') as f:
                f.write(http_context.query['file'])
            http_context.respond('200 OK')
        return ''

    @url(r'/api/lmn/smbclient/finish-upload')
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
        home = AuthenticationService.get(self.context).get_provider().get_profile(user)['homeDirectory']
        upload_dir = f'{home}\\.upload'

        for file in files:
            name = file['name'].replace('/', '')
            path = file['path']
            id = file['id']
            chunk_dir = f'{upload_dir}\\upload-{id}'

            target = f'{path}\\{name}'
            with smbclient.open_file(target, mode='wb') as f:
                for i in range(len(smbclient.listdir(chunk_dir))):
                    chunk_file = f'{chunk_dir}\\{str(i+1)}'
                    with smbclient.open_file(chunk_file, mode='rb') as chunk:
                        f.write(chunk.read())
                    smbclient.remove(chunk_file)

            smbclient.rmdir(chunk_dir)

            targets.append(target)
        return targets


    # @url(r'/api/lmn/smbclient/read/(?P<path>.+)')
    # @authorize('smbclient:read')
    # @endpoint(api=True)
    # def handle_api_fs_read(self, http_context, path=None):
    #     """
    #     Return the content of a file on the filesystem.
    #
    #     :param http_context: HttpContext
    #     :type http_context: HttpContext
    #     :param path: Path of the file
    #     :type path: string
    #     :return: Content of the file
    #     :rtype: string
    #     """
    #
    #     if not os.path.exists(path):
    #         http_context.respond_not_found()
    #         return 'File not found'
    #     try:
    #         content = open(path, 'rb').read()
    #         if http_context.query:
    #             encoding = http_context.query.get('encoding', None)
    #             if encoding:
    #                 content = content.decode(encoding)
    #         return content
    #     except OSError as e:
    #         http_context.respond_server_error()
    #         return json.dumps({'error': str(e)})
    #
    # @url(r'/api/lmn/smbclient/write/(?P<path>.+)')
    # @authorize('smbclient:write')
    # @endpoint(api=True)
    # def handle_api_fs_write(self, http_context, path=None):
    #     """
    #     Write content (method post) to a specific file given with path.
    #     Method POST.
    #
    #     :param http_context: HttpContext
    #     :type http_context: HttpContext
    #     :param path: Path of the file
    #     :type path: string
    #     """
    #
    #     try:
    #         content = http_context.body
    #         if http_context.query:
    #             encoding = http_context.query.get('encoding', None)
    #             if encoding:
    #                 content = content.decode('utf-8')
    #         with open(path, 'w') as f:
    #             f.write(content)
    #     except OSError as e:
    #         raise EndpointError(e)



    #
    # @url(r'/api/lmn/smbclient/chmod/(?P<path>.+)')
    # @authorize('smbclient:write')
    # @endpoint(api=True)
    # def handle_api_fs_chmod(self, http_context, path=None):
    #     """
    #     Change mode for a specific file.
    #
    #     :param http_context: HttpContext
    #     :type http_context: HttpContext
    #     :param path: Path of file
    #     :type path: string
    #     """
    #
    #     if not os.path.exists(path):
    #         raise EndpointReturn(404)
    #     data = json.loads(http_context.body.decode())
    #     try:
    #         os.chmod(path, data['mode'])
    #     except OSError as e:
    #         raise EndpointError(e)
    #
    # @url(r'/api/lmn/smbclient/create-file/(?P<path>.+)')
    # @authorize('smbclient:write')
    # @endpoint(api=True)
    # def handle_api_fs_create_file(self, http_context, path=None):
    #     """
    #     Create empty file on specified path.
    #
    #     :param http_context: HttpContext
    #     :type http_context: HttpContext
    #     :param path: Path of file
    #     :type path: string
    #     """
    #
    #     try:
    #         os.mknod(path, int('644', 8))
    #     except OSError as e:
    #         raise EndpointError(e)
    #
    #
