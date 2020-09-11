#!/usr/bin/env bash
curl --data-binary '{"jsonrpc": "2.0", "id":1, "method": "Addons.SetAddonEnabled", "params": { "addonid": "service.pyfoehn", "enabled": true }}' -H 'content-type: application/json;' http://root:PASSWORD@192.168.178.67:8080/jsonrpc
