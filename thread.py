import time
import threading
import concurrent.futures

start = time.perf_counter()

def do_something(seconds):
	print(f'sleeping {seconds} second...')
	time.sleep(seconds)
	return 'done sleeping...'

with concurrent.futures.ThreadPoolExecutor() as executor:
	
	results = [executor.submit(do_something, _) for _ in range(10)]
	# f2 = executor.submit(do_something, 1)
	# f3 = executor.submit(do_something, 1)
	# print(f1.result())
	# print(f2.result())

	for f in concurrent.futures.as_completed(results):
		print(f.result())
	# print(results)

# threads = []


# for _ in range(10):
# 	t = threading.Thread(target=do_something, args=[2])
# 	t.start()
# 	threads.append(t)


# for thread in threads:
# 	thread.join()


finish = time.perf_counter()

print(f'finished in {finish - start} seconds')