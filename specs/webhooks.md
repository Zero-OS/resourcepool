# Webhooks in O-orchestrator

## The need for webhooks

We need a way to provide a way for 3rd parties to be notified when certain events happen.


## Explenation

We provide a new endpoint in the 0-orchestrator API for 3rd parties to register a webhook and on which kind of events he wants to register.
We will store those webhooks as AYS services. 
When a certains event happens we will search in all registered webhooks check if they are registered on the specific event and make a post towards the webhook.
The postdata will include the eventtype a timestamp and optionally extra metdata specific for each eventtype.


## Webhook registration endpoint

```json
POST /webhooks/
{
    "name": "mywebhook",
    "url": "http://mypublicurl.com/webhookhandler",
    "events": ["healtcheck", "qos"]

}
```

```json
GET /webhooks/
["mywebhook"]
```

```json
GET /webhooks/mywebhook
{
    "name": "mywebhook",
    "url": "http://mypublicurl.com/webhookhandler",
    "events": ["healtcheck", "qos"]

}
```

```json
DELETE /webhooks/mywebhook
```

```
PUT /webhooks/mywebhook
{
    "name": "mywebhook",
    "url": "http://mypublicurl.com/webhookhandler",
    "events": ["healtcheck", "qos"]

}
```
