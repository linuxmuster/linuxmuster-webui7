# Linuxmuster Wireguard VPN Manager

## Configuration

You need a configfile like the following:

`/etc/linuxmuster/webui/wireguard/config.json`:
    {
        "url": "http://10.0.0.3:8000",
        "secret": "1234567890"
    }

`/etc/linuxmuster/webui/config.yml`:
    linuxmuster:
        [...]
        display:
            show_wireguard: true
