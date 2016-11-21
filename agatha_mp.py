from multiprocessing import Process, Queue, freeze_support
import uuid
import random



def test_worker(work_q, out_q, worker_number):
    blocks_done = 0
    total_random = 0.0
    while True:
        # While there is still work on the queue...
        work_block = work_q.get()
        blocks_done += 1
        if work_block is None:
            # There is no work for me left to do
            break

        """print("Hello I am worker %d, looking at block %s with random number %f" % (
            worker_number,
            work_block["block_id"],
            work_block["a_number"]
        ))"""
        total_random += work_block["a_number"]
    out_q.put({
        "mean_random": total_random / blocks_done,
        "blocks_done": blocks_done,
        "worker_i": worker_number,
    })

if __name__ == "__main__":
	freeze_support()
	
	N_PROCESSES = 10
	work_queue = Queue()
	out_queue = Queue()

	# Make some work to do
	for i in range(200000):
		work_queue.put({
			"block_id": str(uuid.uuid4()),
			"a_number": random.random()*100,
		})

	# Make processes, give them the work_queue
	processes = []
	for worker_i in range(N_PROCESSES):
		p = Process(
				target=test_worker,
				args=(work_queue, out_queue, worker_i)
		)
		processes.append(p)

	# Start processes
	for p in processes:
		p.start()

	# Add sentinels to work queue
	# These None's will cause a test_worker to stop
	for i in range(N_PROCESSES):
		work_queue.put(None)

	# NOTE This code blocks until ALL processes have completed work...
	for p in processes:
		p.join()

	# Process some results...
	while not out_queue.empty():
		out_block = out_queue.get()
		print("Worker %d handled %d blocks. Random average number was %.2f" % (
			out_block["worker_i"],
			out_block["blocks_done"],
			out_block["mean_random"],
		))