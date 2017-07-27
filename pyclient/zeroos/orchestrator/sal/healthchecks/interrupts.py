import time
from ..healthcheck import HealthCheckRun

descr = """
Monitors if a network bond (if there is one) has both (or more) interfaces properly active.
"""


class Interrupts(HealthCheckRun):
    ID = 'interrupts'

    def __init__(self, warn=8000, error=1000):
        super().__init__()
        self._warn = warn
        self._error = error
        self.result['id'] = 'interrupts'
        self.result['name'] = 'CPU Interrupts'
        self.result['category'] = 'Hardware'

    def _get(self, node):
        client = node.client

        state = client.aggregator.query('machine.CPU.interrupts').get('machine.CPU.interrupts')
        if state is None:
            # nothing to check yet
            return {
                'id': self.ID,
                'status': 'WARNING',
                'text': 'Number of interrupts per second is not collected yet',
            }

        # time of last reported value
        last_time = state['last_time']
        current = state['current']['300']
        # start time of the current 5min sample
        current_time = current['start']
        if current_time < time.time() - (10*60):
            return {
                'id': self.ID,
                'status': 'WARNING',
                'text': 'Last collected interrupts are too far in the past',
            }

        # calculate avg per second
        value = current['avg'] / (last_time - current_time)

        status = 'OK'
        text = 'Interrupts are okay'

        if value >= self._error:
            status = 'ERROR'
            text = 'Interrupts exceeded error threshold of {} ({})'.format(self._error, value)
        elif value >= self._warn:
            status = 'WARNING'
            text = 'Interrupts exceeded warning threshold of {} ({})'.format(self._warn, value)

        return {
            'id': self.ID,
            'status': status,
            'text': text,
        }

    def run(self, node):
        self.result['messages'].append(self._get(node))