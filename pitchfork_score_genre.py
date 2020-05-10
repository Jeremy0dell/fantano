import csv
from pitchfork import search

csv_list = []

with open('fantano_artists_titles.csv', newline='') as csvfile:
	reader = csv.reader(csvfile, delimiter='^', quotechar='|')
	for row in reader:
		csv_list.append(row)

with open('scores_genres.csv', 'w', newline='') as csvfile:
	fieldnames = ['score', 'genres']
	writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
	writer.writeheader()

	for row in csv_list[1:]:
		print(row[0], row[1])
		try:
			a = search(row[0], row[1])
			print(a)
			writer.writerow({'score': a.score(), 'genres': a.genres()})
		except IndexError as e:
			print(e)
			writer.writerow({'score': 'err: '+ row[0], 'genres': 'err: '+ row[1]})
