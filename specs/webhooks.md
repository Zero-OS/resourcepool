# Webhooks in 0-orchestrator

## The need for webhooks

We need a way to provide a way for 3rd parties to be notified when certain events happen.


## Explanation

We provide a new endpoint in the 0-orchestrator API for 3rd parties to register a webhook and on which event types they want to register.
We will store those webhooks as AYS services. 
When a certain event happens we will search in all registered webhooks check if they are registered on the specific event type and make a post towards the webhook.
The postdata will include the eventtype, event,  a timestamp and optionally extra metdata specific for each eventtype.

Each eventype will have different sub events. For example for eventtype `ork`, we can have events `VM_SHUTDOWN`, `VM_QUARANTINE`.
A webhook will register to an eventtype and orchestrator will post all events of this eventtype to the webooh.

## Webhook registration endpoint

```json
POST /webhooks/
{
    "name": "mywebhook",
    "url": "http://mypublicurl.com/webhookhandler",
    "eventtypes": ["healtcheck", "ork"]

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
    "eventtypes": ["healtcheck", "ork"]

}
```

```json
DELETE /webhooks/mywebhook
```

```json
PUT /webhooks/mywebhook
{
    "url": "http://mypublicurl.com/webhookhandler",
    "eventtypes": ["healtcheck", "qos"]

}
```

