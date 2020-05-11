import csv
import threading
import concurrent.futures
from pitchfork import search

def query(artist, title):
	print(artist, title)
	try:
		a = search(artist, title if title != 'Self-Titled' else artist)
		print(a)
		writer.writerow({'artist': artist, 'album': title, 'score': a.score(), 'genres': a.genres()})
	except IndexError as e:
		print(e)
		writer.writerow({'artist': artist, 'album': title, 'score': 'SCORE ERROR', 'genres': 'GENRES ERROR'})


csv_list = []
threads = []

with open('fantano.csv', newline='') as csvfile:
	reader = csv.reader(csvfile, delimiter='^', quotechar='|')
	for row in reader:
		csv_list.append(row)

with open('scores_genres.csv', 'w', newline='') as csvfile:
	fieldnames = ['artist', 'album', 'score', 'genres']
	writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
	writer.writeheader()

	with concurrent.futures.ThreadPoolExecutor() as executor:
		results = [executor.submit(query, row[0], row[1]) for row in csv_list[1:]]

		for f in concurrent.futures.as_completed(results):
			print(f.result())

		# for row in csv_list[1:]:
		# 	# TODO: change 'self-titled' to artist name
		# 	# TODO: switch to concurrent futures from tutorial
		# 	t = threading.Thread(target=query, args=(row[0], row[1]))
		# 	t.start()
		# 	threads.append(t)

		# for thread in threads:
		# 	thread.join()