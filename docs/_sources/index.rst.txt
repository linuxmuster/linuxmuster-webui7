.. linuxmuster-webui7 documentation 

Linuxmuster-webui7's developer documentation
============================================

.. autosummary::
   :toctree: _autosummary
   :recursive:
   :caption: Contents:

About
-----

Welcome in this API reference documentation !

Linuxmuster-webui7 is a part of the `linuxmuster.net <https://www.linuxmuster.net/de/home/>`_'s project which provides a complete environment for school network management.

You can find the whole description of the install process on the `official documentation page <https://docs.linuxmuster.net/de/latest/>`_ of the project.

In particularly, some `appliances (Proxmox, XCP-ng and KVM) are prepared <https://docs.linuxmuster.net/de/latest/getting-started/installoptions/index.html>`_ in order to permit a fast deployment for test use.

Ajenti
------

Linuxmuster-webui7 is based on the server admin panel `Ajenti <https://github.com/ajenti/ajenti/tree/master>`_ and only adds some plugins for a complete integration into a linuxmuster.net environment. The plugins are written in `Python <https://www.python.org/>`_ and `AngularJS <https://angularjs.org/>`_.

If you want to learn or contribute to this project, you need first to be ease with `Ajenti's install and dev documentation <http://docs.ajenti.org/en/latest/index.html>`_.

This documentation only lists an API reference for the specific plugins in linuxmuster.net.

.. toctree::
   :maxdepth: 1
   :caption: Users
   :hidden:

.. toctree::
   :maxdepth: 1
   :caption: Plugins
   :hidden:

   plugins/lmn_auth.rst

.. toctree::
   :maxdepth: 1
   :caption: Python API
   :hidden:

   python/lmn_auth.rst
   python/lmn_common.rst
   python/lmn_crontab.rst
   python/lmn_devices.rst
   python/lmn_dhcp.rst
   python/lmn_docker.rst
   python/lmn_groupmembership.rst
   python/lmn_landingpage.rst
   python/lmn_linbo.rst
   python/lmn_linbo4.rst
   python/lmn_linbo_sync.rst
   python/lmn_quotas.rst
   python/lmn_session.rst
   python/lmn_settings.rst
   python/lmn_setup_wizard.rst
   python/lmn_users.rst

