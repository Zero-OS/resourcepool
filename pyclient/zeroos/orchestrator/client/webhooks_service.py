class WebhooksService:
    def __init__(self, client):
        self.client = client



    def DeleteWebhook(self, webhookname, headers=None, query_params=None, content_type="application/json"):
        """
        Delete a webhook
        It is method for DELETE /webhooks/{webhookname}
        """
        uri = self.client.base_url + "/webhooks/"+webhookname
        return self.client.delete(uri, None, headers, query_params, content_type)


    def GetWebhook(self, webhookname, headers=None, query_params=None, content_type="application/json"):
        """
        Get a webhook
        It is method for GET /webhooks/{webhookname}
        """
        uri = self.client.base_url + "/webhooks/"+webhookname
        return self.client.get(uri, None, headers, query_params, content_type)


    def UpdateWebhook(self, data, webhookname, headers=None, query_params=None, content_type="application/json"):
        """
        Update a webhook
        It is method for PUT /webhooks/{webhookname}
        """
        uri = self.client.base_url + "/webhooks/"+webhookname
        return self.client.put(uri, data, headers, query_params, content_type)


    def ListWebhooks(self, headers=None, query_params=None, content_type="application/json"):
        """
        List all webhooks
        It is method for GET /webhooks
        """
        uri = self.client.base_url + "/webhooks"
        return self.client.get(uri, None, headers, query_params, content_type)


    def CreateWebhook(self, data, headers=None, query_params=None, content_type="application/json"):
        """
        Create Webhook
        It is method for POST /webhooks
        """
        uri = self.client.base_url + "/webhooks"
        return self.client.post(uri, data, headers, query_params, content_type)
