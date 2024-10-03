import json
import time
from isabelle_client import start_isabelle_server, get_isabelle_client


class Isabelle:
    def __init__(self,
                 isabelle_name='test',
                 port=8887,
                 log_file='server.log',
                 session_name='HOL',
                 dirs=None,
                 verbose=True,
                 options=None,
                 watchdog_timeout=60):
        self.isabelle_name = isabelle_name
        self.port = port
        self.log_file = log_file
        self.session_name = session_name
        self.dirs = dirs if dirs is not None else ['./Isabelle2023']
        self.verbose = verbose
        self.options = options if options is not None else []
        self.watchdog_timeout = watchdog_timeout
        self._init_client()
        self._init_session()

    def _init_client(self):
        start_time = time.time()
        server_info, _ = start_isabelle_server(name=self.isabelle_name, port=self.port, log_file=self.log_file)
        self.isabelle = get_isabelle_client(server_info)
        print(f'Isabelle server started with info: {server_info} in {time.time() - start_time:.2f}s.')

    def _init_session(self):
        start_time = time.time()
        self.isabelle.session_build(session=self.session_name, dirs=self.dirs, verbose=self.verbose,
                                    options=self.options)
        self.session_id = self.isabelle.session_start(session=self.session_name)
        print(f'Isabelle session started in {time.time() - start_time:.2f}s.')

    def get_response(self, theories, master_dir):
        start_time = time.time()
        isabelle_response = self.isabelle.use_theories(session_id=self.session_id,
                                                       theories=theories,
                                                       master_dir=master_dir,
                                                       watchdog_timeout=self.watchdog_timeout)
        inference_time = time.time() - start_time
        return isabelle_response, inference_time

    @staticmethod
    def check_error(isabelle_response):
        error_details = []
        error_lines = []

        finished_response = next((item for item in isabelle_response if item.response_type == 'FINISHED'), None)

        if finished_response:
            response_body = json.loads(finished_response.response_body)
            if response_body['ok']:
                is_valid = True
                if len(response_body['errors']) != 0:
                    print('Isabelle server command \"use_theories\" did not act as expected.')
                    is_valid = False
            else:
                is_valid = False

            for error in response_body['errors']:
                message = error['message']
                pos = error['pos']
                line, offset, end_offset = pos['line'], pos['offset'], pos['end_offset']
                error_details.append(f'Error on line {line}, start {offset}, end {end_offset}: {message}')
                error_lines.append(line)

        else:
            print('Not Finished.')
            is_valid = False
        return is_valid, error_lines, error_details

    def shutdown(self):
        self.isabelle.session_stop(session_id=self.session_id)
        self.isabelle.shutdown()
        print('Isabelle session is shut down.')

    def restart(self):
        self._init_client()
        self._init_session()
