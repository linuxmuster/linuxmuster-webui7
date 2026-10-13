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

   plugins/lmn_auth
   plugins/lmn_clients
   plugins/lmn_common
   plugins/lmn_crontab
   plugins/lmn_device-manager
   plugins/lmn_devices
   plugins/lmn_dhcp
   plugins/lmn_docker
   plugins/lmn_groupmembership
   plugins/lmn_landingpage
   plugins/lmn_linbo4
   plugins/lmn_linbo_sync
   plugins/lmn_links
   plugins/lmn_nextcloud
   plugins/lmn_permissions
   plugins/lmn_quotas
   plugins/lmn_samba_dns
   plugins/lmn_samba_shares
   plugins/lmn_session_new
   plugins/lmn_settings
   plugins/lmn_setup_wizard
   plugins/lmn_smbclient
   plugins/lmn_users
   plugins/lmn_vdi_administration
   plugins/lmn_vdi_dashboard
   plugins/lmn_w_datetime
   plugins/lmn_websession
   plugins/lmn_wireguard

.. toctree::
   :maxdepth: 1
   :caption: Python API
   :hidden:

   autoapi/index

