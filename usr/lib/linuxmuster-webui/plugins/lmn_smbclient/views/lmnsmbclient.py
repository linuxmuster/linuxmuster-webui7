"""
Tools to handle files, directories and uploads.
"""
import base64
import logging
import os
import re
import subprocess
import tempfile
import pexpect
import smbclient
import gevent
import pwd
from zipfile import ZipFile
from urllib.parse import quote, unquote
from smbprotocol.exceptions import SMBOSError, NotFound, SMBAuthenticationError, InvalidParameter, SMBException
from spnego.exceptions import BadMechanismError
from jadi import component

from aj.api.http import url, get, post, HttpPlugin
from aj.api.endpoint import endpoint, EndpointError, EndpointReturn
from aj.auth import authorize, AuthenticationService
from aj.plugins.lmn_common.mimetypes import content_mimetypes, content_filetypes


# TODO
# - Better error management (directory not empty, errors in promise list, ... )
# - Test encoding Windows
# - download selected resources as zip
# - UPLOAD non empty directory

# Wrapper for smbclient methods in order to avoid empty credits error
def credit_wrapper(func):
    def new_func(*args, **kwargs):
        retry = 0
        while retry < 10:
            try:
                return func(*args, **kwargs)
            except SMBException as e:
                if '0 credits are available' in str(e):
                    retry += 1
                    gevent.sleep(2)
                else:
                    raise
        # 5 attempts was not enough ?
        raise EndpointError("Still not enough credits to create working directory after five attempts. Please contact your administrator.")
    return new_func

for method in ['copyfile', 'rename', 'makedirs', 'mkdir', 'renames', 'remove', 'removedirs']:
    setattr(smbclient, method, credit_wrapper(getattr(smbclient, method)))


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
        user_context = {
            'user': user,
            'role': profil['sophomorixRole'],
            'adminclass': profil['sophomorixAdminClass'],
            'home': profil['homeDirectory'],
        }
        return self.context.schoolmgr.get_shares(user_context)

    @post(r'/api/lmn/smbclient/list')
    @endpoint(api=True)
    def handle_api_smb_list(self, http_context):
        """
        Return a list of objects (files, directories, ...) in a specific samba
        share.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: All items with informations
        :rtype: dict
        """

        path = http_context.json_body().get('path', None)
        return self._smb_list_path(path)

    @post(r'/api/lmn/smbclient/listhome')
    @endpoint(api=True)
    def handle_api_smb_listhome(self, http_context):
        """
        Return a list of objects (files, directories, ...) from a specific
        user's home.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: All items with informations
        :rtype: dict
        """

        user = http_context.json_body().get('user', self.context.identity)
        homepath = self.context.ldapreader.get(f'/users/{user}', dict=False).homeDirectory
        return self._smb_list_path(homepath)


    def _smb_list_path(self, path):
        """
        Return a list of objects (files, directories, ...) from a specific path.

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

        try:
            items = []
            for item in smbclient.scandir(path):
                item_path = os.path.join(path, item.name) # TODO
                ext = os.path.splitext(item.name)[1]

                data = {
                    'name': item.name,
                    'path': item_path,
                    'download_url': base64.b64encode(item_path.encode('utf-8'), altchars=b'-_').decode(),
                    'unixPath': SMB2UnixPath(item_path),
                    'isDir': item.is_dir(),
                    'isFile': item.is_file(),
                    'isLink': item.is_symlink(),
                    'filetype': content_filetypes.get(ext, 'file'),
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
        except SMBOSError as e:
            raise EndpointError(f"{path} does not seem to exist.")
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
            if smbclient.path.isfile(src):
                smbclient.copyfile(src, dst)
            elif smbclient.path.isdir(src):
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
            # First pass : delete files
            for item in smbclient.walk(path):
                # item like (SMBPATH, [List of subdir], [List of files])
                smbpath = item[0]
                for file in item[2]:
                    smbclient.unlink(f"{smbpath}\\{file}")

            # Second pass : delete directories from bottom
            for directory in smbclient.walk(path, topdown=False):
                smbclient.rmdir(directory[0])
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
        user_context = {
            'user': user,
            'role': profil['sophomorixRole'],
            'adminclass': profil['sophomorixAdminClass'],
            'home': profil['homeDirectory'],
        }
        home = self.context.schoolmgr.get_homepath(user_context)
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
        user_context = {
            'user': user,
            'role': profil['sophomorixRole'],
            'adminclass': profil['sophomorixAdminClass'],
            'home': profil['homeDirectory'],
        }
        home = self.context.schoolmgr.get_homepath(user_context)
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
        user_context = {
            'user': user,
            'role': profil['sophomorixRole'],
            'adminclass': profil['sophomorixAdminClass'],
            'home': profil['homeDirectory'],
        }
        home = self.context.schoolmgr.get_homepath(user_context)
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
            
            try:
                smbclient.rmdir(chunk_dir)
            except AttributeError as e:
                # See https://github.com/jborean93/smbprotocol/issues/269
                logging.warning(f"Was not able to delete {chunk_dir}, bug of smbprotocol ?")

            targets.append({
                'name': name,
                'path': target,
                'unixPath': '',
                'isDir': False,
                'isFile': True,
                'isLink': False,
            })
        return targets

    @get(r'/api/lmn/smbclient/download')
    @endpoint(page=True)
    def handle_smb_download(self, http_context):
        q = http_context.query.get('path', None)
        path = base64.b64decode(q, altchars=b'-_').decode('utf-8')

        if '..' in path:
            return http_context.respond_forbidden()

        try:
            isfile = smbclient.path.isfile(path)
            isdir = smbclient.path.isdir(path)
            # Head request to handle 404 in Angular
            if http_context.method == 'HEAD':
                http_context.respond('200 OK')
                return ''
        except (ValueError, SMBOSError, NotFound):
            http_context.respond_not_found()
            return

        name = path.split('/')[-1]

        if isfile:
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

            http_context.add_header('Content-Disposition', (f'attachment; filename="{quote(name)}"'))

            yield http_context.gzip(content)

        if isdir:
            zip_name = f'{quote(name)}.zip'
            tmp_dir = tempfile.mkdtemp()
            zip_path = f'{tmp_dir}/{zip_name}'

            with ZipFile(zip_path, 'w') as zip_obj:
                for root, folders, files in smbclient.walk(path):
                    for f in files:
                        relative_path = root.replace(path, '').replace('\\', '/')[1:]
                        relative_path = f"{relative_path}/{f}"
                        smb_path = f"{root}\\{f}"
                        with smbclient.open_file(smb_path, 'rb') as file_io:
                            content = file_io.read()
                        zip_obj.writestr(relative_path, content)

            http_context.add_header('Content-Type', 'application/zip')
            http_context.add_header('Content-Disposition', (f'attachment; filename="{zip_name}"'))

            with open(zip_path, 'rb') as zip_tmp:
                content = zip_tmp.read()
            yield http_context.gzip(content)

            os.unlink(zip_path)
            os.rmdir(tmp_dir)

    @post(r'/api/lmn/smbclient/refresh_krbcc')
    @endpoint(api=True)
    def handle_smb_refresh_krbcc(self, http_context):
        username = self.context.identity
        uid = pwd.getpwnam(username).pw_uid
        pw = http_context.json_body()['pw']
        subprocess.check_output(['/usr/bin/kdestroy', '-c', f'/tmp/krb5cc_{uid}'])
        try:
            child = pexpect.spawn('/usr/bin/kinit', ['-c', f'/tmp/krb5cc_{uid}', username])
            child.expect('.*:', timeout=2)
            child.sendline(pw)
            child.expect(pexpect.EOF)
            child.close()
            exit_code = child.exitstatus
            if exit_code:
                logging.error(f"Was not able to initialize Kerberos ticket for {username}")
                msg = f"{child.before.decode().strip()}"
                logging.error(msg)
                return {'type': "error", 'msg':msg}
            # Be sure to reset all cache connection and reload the new ticket
            smbclient.reset_connection_cache()
            return {'type': "output", 'msg': _("Ticket successfully refreshed")}
        except pexpect.exceptions.TIMEOUT:
            logging.error(f"Was not able to initialize Kerberos ticket for {username}")
            return {'type': "error", 'msg': _("Timeout while trying to get a kerberos ticket")}

    @post(r'/api/lmn/smbclient/createSessionWorkingDirectory')
    @endpoint(api=True)
    def handle_api_create_working_dir(self, http_context):
        """
        Create a working directory for each user in a session with path `user/transfer/TEACHERNAME/_collect`.
        """

        users = http_context.json_body()['users']
        if isinstance(users, str):
            users = [users]

        errors = {'global':''}

        for user in users:
            if user is None:
                continue

            if user.endswith('-exam'):
                user_data = self.context.ldapreader.get(f'/users/exam/'
                                                        f'{user}', attributes=['homeDirectory', 'sophomorixAdminClass', 'sophomorixRole'])
            else:
                user_data = self.context.ldapreader.get(f'/users/{user}', attributes=['homeDirectory', 'sophomorixAdminClass', 'sophomorixRole'])

            homeDirectory, schoolclass = user_data['homeDirectory'], user_data['sophomorixAdminClass']
            path = f'{homeDirectory}/transfer/{self.context.identity}/_collect'

            try:
                if not smbclient.path.isdir(path):
                    smbclient.makedirs(path)
            except SMBOSError as e:
                if 'NtStatus 0xc0000035' in str(e):
                    pass # Should not appear again
                elif 'STATUS_ACCESS_DENIED' in str(e):
                    errors[user] = f"{self.context.identity} is not member of the group {schoolclass}."
                elif 'STATUS_DISK_FULL' in str(e):
                    errors['global'] = "Your quota is full, please free some space in order to share files."
                else:
                    errors[user] = str(e)
            except (ValueError, NotFound) as e:
                errors[user] = str(e)
            except InvalidParameter as e:
                errors[user] = f'Problem with path {path} : {str(e)}'

        return errors

    @post(r'/api/lmn/smbclient/listCollectDir')
    @endpoint(api=True)
    def handle_api_list_collect_dir(self, http_context):
        """
        List content of `user/transfer/TEACHERNAME/_collect` for each participants.
        """

        participants = http_context.json_body()['participants']

        files = {}

        for participant in participants:
            cn = participant['cn']
            collect_path = f"{participant['homeDirectory']}/transfer/{self.context.identity}/_collect"

            try:
                if not smbclient.path.isdir(collect_path):
                    smbclient.makedirs(collect_path)

                files[cn] = self._smb_list_path(collect_path)

            except SMBOSError as e:
                if 'NtStatus 0xc0000035' in str(e):
                    pass # Should not appear again
                elif 'STATUS_ACCESS_DENIED' in str(e):
                    if participant['sophomorixAdminClass'] != 'teachers':
                        files[cn] = f"{self.context.identity} is not member of the group {participant['sophomorixAdminClass']}."
                else:
                    files[cn] = e
            except (ValueError, NotFound) as e:
                files[cn] = e
            except InvalidParameter as e:
                files[cn] = f'Problem with path {collect_path} : {e}'

        return files