import queue
import threading

import requests


class HyperlinkAvailabilityCheckWorker(threading.Thread):
    def __init__(self, rqueue, wqueue) -> None:
        self.rqueue = rqueue
        self.wqueue = wqueue
        self._session = requests.Session()
        super().__init__(daemon=True)

    def run(self) -> None:
        while True:
            uri = self.wqueue.get()
            if not uri:
                self._session.close()
                break

            self._session.request(
                'HEAD',
                url=uri,
                timeout=30,
                verify=True,
            )
            self.rqueue.put(uri)
            self.wqueue.task_done()


def test_crash():
    for i in range(1_000):
        print(f'loop: {i}')

        # setup
        rqueue = queue.Queue()
        wqueue = queue.Queue()
        workers: list[HyperlinkAvailabilityCheckWorker] = []

        # invoke threads
        num_workers = 2
        for _ in range(num_workers):
            thread = HyperlinkAvailabilityCheckWorker(rqueue, wqueue)
            thread.start()
            workers.append(thread)

        # check
        total_links = 0
        for hyperlink in (
            'https://python.org/dev/',
            'https://peps.python.org/pep-0008/',
        ):
            wqueue.put(hyperlink, False)
            total_links += 1

        done = 0
        while done < total_links:
            result = rqueue.get()
            print(result)
            done += 1

        # shutdown_threads
        wqueue.join()
        for _worker in workers:
            wqueue.put('', False)


if __name__ == '__main__':
    import sys

    print(f'GIL enabled?: {sys._is_gil_enabled()}')
    print()
    test_crash()
