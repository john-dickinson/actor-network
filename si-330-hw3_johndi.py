from bs4 import BeautifulSoup as bs
import json
import urllib2 as u
import re
import time
import pydot
import ast

def parse_text(in_file, output_file):
	try:
		response = open(in_file)
	except: 
		print "Invalid input file."
	html_doc = response.read()
	soup = bs(html_doc)
	rows = soup.find_all('tr')
	is_firstline = True
	count = 0
	id_list = []
	for item in rows:
		if count < 100:
			try:
				outfile = open(output_file,'a')
			except:
				print "Invalid output file."
			if is_firstline:
				is_firstline = False
				continue
			data = item.find_all('td')
			rank = data[0].string
			rank = rank.strip('.')
			link = data[2].find('a', href=re.compile('/title/[a-z]+[0-9]+'))
			title = link.string
			year = data[2].find("span", {'class':'year_type'})
			year = year.string
			movie_id = link.get('href')
			movie_id = movie_id.strip('/title/')
			movie_id = movie_id.strip('/')
			movie_id = "tt" + movie_id
			id_list.append(movie_id)
			value = movie_id + "\t" + rank + "\t" + title + " " + year + "\n"
			value = value.encode('utf-8')
			outfile.write(value)
			count += 1
			outfile.close()
	return id_list

def metadata(id_list,output_file):
	for item in id_list:
		try:
			url = ('http://www.omdbapi.com/?i=' + item)
			response = u.urlopen(url)
		except:
			print "Could not read in the list from the URL."
		try:
			outfile = open(output_file,'a')
		except:
			print "Could not open the output file."
		html_doc = response.read() + "\n"
		outfile.write(html_doc)
		time.sleep(5)
		outfile.close()

def parse_json(in_file, output_file):
	try:
		json_file = open(in_file,'rU')
	except:
		print "JSON Input file could not be opened"
	for item in json_file:
		outfile = open(output_file,'a')
		this = json.loads(item)
		title = this['Title']
		actors = this['Actors']
		actors = actors.encode('utf-8')
		actors = actors.split(', ')
		value = title + "\t" + str(actors) + "\n"
		outfile.write(value.encode('utf-8'))
	json_file.close()

def write_html(url,output_file):
	try:
		response = u.urlopen(url)
	except:
		print "Invalid URL"
	html_doc = response.read()
	out_file = open(output_file, 'wb')
	out_file.write(html_doc)
	out_file.close()

def graphing(input_file):
	in_file = open(input_file,'rU')
	my_dict = {}
	graph = pydot.Dot(graph_type='digraph')
	for item in in_file:
		item = item.split("\t")
		my_list = item[1]
		my_list = ast.literal_eval(my_list)
		graph.add_edge(pydot.Edge(my_list[0], my_list[1]))
		graph.add_edge(pydot.Edge(my_list[0], my_list[2]))
		graph.add_edge(pydot.Edge(my_list[0], my_list[3]))
		graph.add_edge(pydot.Edge(my_list[1], my_list[2]))
		graph.add_edge(pydot.Edge(my_list[1], my_list[3]))
		graph.add_edge(pydot.Edge(my_list[2], my_list[3]))
	graph.write('actors_graph_output.dot')

def main():
	test = write_html('http://www.imdb.com/search/title?at=0&sort=num_votes&count=100', 'step1.html')
	parse_test = parse_text('step1.html','step2.txt')
	test_list = metadata(parse_test,'step3.txt')
	parse_json('step3.txt','step4.txt')
	graphing('step4.txt')

if __name__ == '__main__':
	import profile
	profile.run("main()")