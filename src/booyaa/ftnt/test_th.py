import threading
import queue
import time
from typing import Any, Callable

class ThreadRunner:
    def __init__(self, worker_fn: Callable[[Any, threading.Event], Any],
        concurrency: int = 5, daemon: bool = False):

        self.worker_fn = worker_fn
        self.concurrency = concurrency
        self.daemon = daemon
        self.stop = threading.Event()
        self.q: queue.Queue[Any | None] = queue.Queue()
        self.results: queue.SimpleQueue[tuple[Any, Any]] = queue.SimpleQueue()
        self.threads: list[threading.Thread] = []

    def start(self):
        def _worker():
            while not self.stop.is_set():
                item = self.q.get()
                try:
                    if item is None:  # 番兵
                        return
                    res = self.worker_fn(item, self.stop)
                    self.results.put((item, res))
                except Exception as e:
                    # ログ・計測・再キューなどお好みで
                    self.results.put((item, e))
                finally:
                    self.q.task_done()

        for i in range(self.concurrency):
            t = threading.Thread(target=_worker, name=f"wrk-{i}", daemon=self.daemon)
            t.start()
            self.threads.append(t)

    def submit(self, item: Any):
        self.q.put(item)

    def shutdown(self, timeout: float | None = None):
        # 停止要求＋番兵投入
        self.stop.set()
        for _ in self.threads:
            self.q.put(None)
        # キュー排出待ち
        self.q.join()
        # ワーカー合流（タイムアウト可）
        start = time.time()
        for t in self.threads:
            remain = None if timeout is None else max(0.0, timeout - (time.time() - start))
            t.join(remain)

# 使い方（self.run を既にお持ちならラップするだけ）
def run_wrapper(target_info, stop_event: threading.Event):
    # ループ/ステップの合間で停止判定
    # 例：I/Oはtimeout付けて、復帰時に stop_event を見る
    # if stop_event.is_set(): return
    return self.run(target_info)  # 既存ロジック

runner = ThreadRunner(worker_fn=run_wrapper, concurrency=5, daemon=False)
runner.start()
for ti in self.target_info_list:
    runner.submit(ti)
# …どこかで終了要求が来たら
runner.shutdown(timeout=10.0)
