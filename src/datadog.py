from logging import StreamHandler
from datadog_api_client import ApiClient, Configuration
from datadog_api_client.v2.api.logs_api import LogsApi
from datadog_api_client.v2.model.content_encoding import ContentEncoding
from datadog_api_client.v2.model.http_log import HTTPLog
from datadog_api_client.v2.model.http_log_item import HTTPLogItem

class DatadogHandler(StreamHandler):

    def __init__(self, configuration: Configuration):
        StreamHandler.__init__(self)
        self.configuration = configuration

        with ApiClient(self.configuration) as api_client:
            self.api_instance = LogsApi(api_client)

    def emit(self, record):
        msg = self.format(record)

        body = HTTPLog(
            [
                HTTPLogItem(
                    ddsource="nginx",
                    ddtags="env:prod,version:0.1.1",
                    hostname="railway-okgpt-prod",
                    message=msg,
                    service="bot",
                ),
            ]
        )

        self.api_instance.submit_log(content_encoding=ContentEncoding.DEFLATE, body=body)