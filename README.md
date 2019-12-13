Doghouse
=======

## Usage 
- `doghouse save` will save your dashboard and monitors to json files in ~/.doghouse. 
- `doghouse sync` will take your dashboards and monitors stored in ~/.doghouse and push them back to Datadog. This merely augments config in Datadog and is not destructive. 

## Credentials
Credentials are read from config.yml located in ~/.doghouse. This is in the form:
```
api_key: <api_key>
app_key: <app_key>
```
If you don't specify this then the CLI will ask you for it and save it there anyway.
