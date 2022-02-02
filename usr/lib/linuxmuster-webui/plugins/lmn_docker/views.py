"""
Simple module to get informations from docker host on 10.0.0.3
"""

from jadi import component
import subprocess
import json

from aj.api.http import url, HttpPlugin
from aj.auth import authorize
from aj.api.endpoint import endpoint, EndpointError

@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context
        # TODO : read config /var/lib/linuxmuster/setup.ini to get docker host ip
        self.docker = ['ssh', '10.0.0.3', 'docker']

    @url(r'/api/lm/docker/which')
    @authorize('lm:docker:list')
    @endpoint(api=True)
    def handle_api_which_docker(self, http_context):
        """
        Test ssh connection and retrieve docker version.
        Store the command line as list in self.docker for use in subprocess

        :param http_context: HttpContext
        :type http_context: HttpContext
        """

        try:
            self.docker = subprocess.check_output(['ssh', '10.0.0.3', 'which', 'docker']).decode().strip()
            self.docker = ['ssh', '10.0.0.3', 'docker']
        except subprocess.CalledProcessError as e:
            raise EndpointError(_('Docker is not installed on this host'))

    @url(r'/api/lm/docker/get_resources')
    @authorize('lm:docker:list')
    @endpoint(api=True)
    def handle_api_resources_docker(self, http_context):
        """
        Retrieve stats informations (memory, cpu, ... ) from docker and load one json per container in a list.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Json informations per container
        :rtype: list of json
        """

        command = self.docker + ['stats', '--format', '\'{{json .}}\'', '--no-stream', '-a']
        return [json.loads(line) for line in subprocess.check_output(command).decode().splitlines()]

    @url(r'/api/lm/docker/get_details')
    @authorize('lm:docker:list')
    @endpoint(api=True)
    def handle_api_details_container(self, http_context):
        """
        Retrieve all informations from docker inspect for one container.
        Method POST.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: All container informations
        :rtype: json
        """

        if http_context.method == 'POST':
            container = http_context.json_body()['container']
            command = self.docker + ['inspect', container, '--format', '\'{{json .}}\'']
            return json.loads(subprocess.check_output(command).decode())

    @url(r'/api/lm/docker/container_command')
    @authorize('lm:docker:change')
    @endpoint(api=True)
    def handle_api_container_stop(self, http_context):
        """
        Some controls for container : start, stop and remove. The hash of the container is sent per POST.
        Method POST.

        :param http_context: HttpContext
        :type http_context: HttpContext
        """

        if http_context.method == 'POST':
            container = http_context.json_body()['container']
            control = http_context.json_body()['control']
            command = self.docker + [control, container]
            try:
                subprocess.check_output(command, stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError as e:
                raise EndpointError(e.output.decode().strip())

    @url(r'/api/lm/docker/list_images')
    @authorize('lm:docker:list')
    @endpoint(api=True)
    def handle_api_list_images(self, http_context):
        """
        List all images contained on the docker host.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: All informations from all images
        :rtype: list of json
        """

        command = self.docker + ['images', '--format', '\'{{json .}}\'', '--no-trunc', '-a']
        images = []
        for line in subprocess.check_output(command).decode().splitlines():
            image = json.loads(line)
            image['hash'] = image['ID'].split(':')[1][:12]
            images.append(image)
        return images

    @url(r'/api/lm/docker/remove_image')
    @authorize('lm:docker:change')
    @endpoint(api=True)
    def handle_api_remove_image(self, http_context):
        """
        Delete one image (given as hash) on the docker host.
        Method POST.

        :param http_context: HttpContext
        :type http_context: HttpContext
        """

        if http_context.method == 'POST':
            image = http_context.json_body()['image']
            command = self.docker + ['rmi', image]
            try:
                subprocess.check_output(command, stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError as e:
                raise EndpointError(e.output.decode().strip())

