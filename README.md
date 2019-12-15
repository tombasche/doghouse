Doghouse
=======

## Usage 
- `doghouse save` will save your dashboard and monitors to json files in ~/.doghouse. 
- `doghouse sync` will take your dashboards and monitors stored in ~/.doghouse and push them back to Datadog. This merely augments config in Datadog and is not destructive. 
- `doghouse list <object_type>` will display a list of resources of a specified type. `dashboard` and `monitor` are both supported here.
- `doghouse configure` will reconfigure the Datadog credentials. Optionally accepts `--api-key` and `--app-key` as options to forgo user input. 
## Credentials
Credentials are read from config.yml located in ~/.doghouse. This is in the form:
```
api_key: <api_key>
app_key: <app_key>
```

First usage of the CLI will ask for credentials if they don't already exist anyway.
