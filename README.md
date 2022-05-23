# Cloudflare API Tool
Simple tool to update Cloudflare DNS records via commandline.

```
Usage:
    cf-api-tool.py get <name>
    cf-api-tool.py delete <name>
    cf-api-tool.py update <name> <type> <content> [--proxy]
    cf-api-tool.py (-h | --help)
    cf-api-tool.py --version

Options:
    -h --help   Show this screen
    --version   Show version
    --proxy     Proxy in case of CNAME (default not)
```

**Installation**
```
pip3 install docopt
pip3 install cloudflare
```

Edit and copy config.ini to ~/.config/cloudflare/config.ini


