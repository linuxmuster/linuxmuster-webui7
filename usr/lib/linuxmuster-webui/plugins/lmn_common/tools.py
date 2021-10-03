"""
Useful common functions for the project.
"""

import paramiko

def testSSH(host, username='root', password='Muster!', port=22):
    """
    Basic connection test with SSH.

    :return: bool result and error type
    :rtype: tuple of bool and string
    """

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=username, password=password)
    except paramiko.ssh_exception.NoValidConnectionsError:
        client.close()
        return (False, f'Unable to connect to {host}')
    except paramiko.ssh_exception.AuthenticationException:
        client.close()
        return (False, 'Authentication failed')
    except paramiko.ssh_exception.SSHException:
        client.close()
        return (False, f'Username {username} unknown')
    client.close()
    return (True, '')

# Tests
# print(testSSH('10.0.0.3')) # true
# print(testSSH('10.0.0.3', password='Muster'))  # auth error
# print(testSSH('10.0.0.3', username='bla'))  # username unknown
# print(testSSH('10.0.0.4')) # conn failed
# print(testSSH('10.0.0.3', username='root', port=2222)) # conn failed
