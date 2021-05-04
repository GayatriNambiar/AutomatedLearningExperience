#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ----------------------------------------------
# LOCAL API 
# ----------------------------------------------

from flask import Flask, request, jsonify
from flask_restful import Resource, Api
#from sqlalchemy import create_engine
from flask_sqlalchemy import SQLAlchemy
import urllib

import math
import numpy as np
from collections import OrderedDict, Counter

from distance import levenshtein, jaccard
from difflib import SequenceMatcher

# ----------------------------------------------
# Create an instance of database engine
# ----------------------------------------------

#e = create_engine("postgresql://{username}:{password}@{hostname}:{port}/{database}".format(
#	username = 'andrewfribush',
#	password = 'Caila123456',
#	hostname = 'aauveli76hxiot.c7b2o1zwdlii.us-east-1.rds.amazonaws.com',
#	port = '5432', 
#	database = 'ebdb'))

#application = Flask(__name__)


application = Flask(__name__)
SQLALCHEMY_DATABASE_URI = "postgresql://andrewfribush:Caila123456@aauveli76hxiot.c7b2o1zwdlii.us-east-1.rds.amazonaws.com:5432/ebdb"
application.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
application.config["SQLALCHEMY_POOL_RECYCLE"] = 299
application.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(application)

api = Api(application)

# ----------------------------------------------
# Knuth-Morris-Pratt 
# find exact match of 'A' in B 
# ----------------------------------------------

def prefix(A,i):
	prefix = A[:i+1]
	prefix_holder = []
	for j in range(1, len(prefix)):
		prefix_holder.append(prefix[:j])
	return prefix_holder

def suffix(A,i):
	suffix = A[:i+1]
	suffix_holder = []
	for j in range(1, len(suffix)):
		suffix_holder.append(suffix[j:])
	return suffix_holder

def kmp_table(A):
	A = A.lower()
	kmp_list = []
	for i in range(len(A)):
		if i == 0:
			kmp_list.append(0)
			i = i+1
		else:
			prefix_i = prefix(A,i)
			suffix_i = suffix(A,i)
			size = len(prefix(A,i))
			diff = []
			for j in range(size):
				for k in range(size):
					if prefix_i[j] == suffix_i[k]:
						common = len(prefix_i[j])
						diff.append(common)
			if diff:
				kmp_list.append(max(diff))
			if not diff:
				kmp_list.append(0)
	return kmp_list

def kmp_search(A,B):
	A = A.lower()
	B = B.lower()
	table = kmp_table(A)
	counter = 0
	i = 0
	j = 0 
	while i <= len(B)-1:
		if B[i] == A[j]:
			i = i+1
			j = j+1
			if j != len(A)-1:
				pass
			elif j == len(A)-1:
				counter = counter + 1
				i = i+1
				j = 0

		elif B[i] != A[j]:
			if table[j] == 0:
				i = i + 1
			else:
				i = i + table[j]
			j = 0
	return counter

# ----------------------------------------------
# Fribush Algorithm
# ----------------------------------------------

def fribush(A,B):
	new_A = A.lower().split()
	new_B = B.lower().split()
	counter = 0
	for i in range(len(new_A)):
		for j in range(len(new_B)):
			if len(new_A[i]) == len(new_B[j]):
				if new_A[i] == new_B[j]:
					counter = counter + 1
	return counter

# ----------------------------------------------
# Term Frequency
# ----------------------------------------------

def tf(A,B):
	new_A = A.lower().split()
	new_B = B.lower().split()
	tf_score = 0
	if new_B:
		for i in range(len(new_A)):
			 term_frequency_i = new_B.count(new_A[i])/float(len(new_B))
			 tf_score = tf_score + term_frequency_i
	if not new_B:
		pass
	return tf_score

# ----------------------------------------------
# Levenshtein Distance Algorithm 
# FATAL: SLOW
# ----------------------------------------------

def levenshtein_algo(A, B):
	A = A.lower().split()
	B = B.lower().split()
	counter = 0
	for i in range(len(A)):
		for j in range(len(B)):
			if levenshtein(A[i], B[j]) < 3:
				counter = counter + 1
	return counter 

# ----------------------------------------------
# Jaccard Distance Algorithm 
# A LOT FASTER THAN Levenshtein
# ----------------------------------------------

def jaccard_algo(A, B):
	A = A.lower().split()
	B = B.lower().split()
	counter = 0
	for i in range(len(A)):
		for j in range(len(B)):
			if jaccard(A[i], B[j]) < .2:
				counter = counter + 1
	return counter 

# ----------------------------------------------
# Combinded Algorithm
# ----------------------------------------------

def darth_vader(A,B):
	A = A.lower()
	new_A = A.split()
	if len(new_A) == 1:
		tf_score = tf(A,B)
		fribush_score = fribush(A,B)
		jaccard_score = jaccard_algo(A,B)
		total_score = 4/20 * tf_score + 8/20 * fribush_score + 8/20 * jaccard_score
	else:
		tf_score = tf(A,B)
		kmp_score = kmp_search(A,B)
		jaccard_score = jaccard_algo(A,B)
		total_score = 4/20 * tf_score + 8/20 * kmp_score + 8/20 * jaccard_score		
	return total_score

# ----------------------------------------------
# Scoring System
# ----------------------------------------------

def logistic(x):
	return 1/2 + (1/2)*(math.tanh(x))

def scoring_algo(A, B, i, type):
	A = A.lower()
	total_score = 0 
	if type == 'Bootcamps':
		title_score = dart_vader(str(A),str(B[i]['title']).lower())
		description_score = darth_vader(str(A),str(B[i]['description']).lower())
		skill_score = darth_vader(str(A),str(B[i]['skill']).lower())          
		total_score = title_score + description_score + skill_score
	elif type == 'Video':
		title_score = darth_vader(str(A),str(B[i]['title']).lower())       
		description_score = darth_vader(str(A),str(B[i]['source']).lower())		 
		total_score = title_score + description_score 
	else:
		title_score = darth_vader(str(A),str(B[i]['title']).lower())
		description_score = darth_vader(str(A), str(B[i]['description']).lower())
		total_score = title_score + description_score	
	return logistic(total_score)

# ----------------------------------------------
# return if nothing
# ----------------------------------------------

def return_if_nothing(rows, skills_interest, type):
	check_list = []
	type_list = ['Course', 'Books', 'Bootcamps', 'Podcast']
	if type in type_list:
		for i in range(0,len(rows)):
			check_list.append(kmp_search(str(skills_interest), str(rows[i]['description']).lower()))
		if sum(check_list) == 0:
			return True
		else: 
			return False
	if type not in type_list:
		for i in range(0,len(rows)):
			check_list.append(fribush(str(skills_interest), str(rows[i]['title']).lower()))
		if sum(check_list) == 0:
			return True
		else: 
			return False

# ----------------------------------------------
# Creating a Dictionary of scores
# e.g {'1': '.1234', ...}
# sort the dictionary by items() reversely 
# and pull keys into a index list
# ----------------------------------------------

def create_index_list(rows, skills_interest, type):
	score_dict = {}
	for i in range(0,len(rows)):
		score = scoring_algo(skills_interest, rows, i, type)
		score_dict[str(i)] = score
	reverse_sorted_dict = OrderedDict(sorted(score_dict.items(), key=lambda t: t[1], reverse=True))
	index_list = list(reverse_sorted_dict.keys())
	return index_list

# ----------------------------------------------
# index_list is created by scoring algorithm 
# and create_index_list creates an index_list
# sorted in an increasing manner of score 
# checking mechanism
# ----------------------------------------------

def feedback(rows, skills_interest, index_list, type):
	feedback_list = []
	type_list = ['Course', 'Books', 'Bootcamps', 'Podcast']
	if type in type_list:
		for k in range(len(index_list)):
			if fribush(str(skills_interest), str(rows[int(index_list[k])]['description'])) == 0:
				pass
			else:
				feedback_list.append(index_list[k])
	if type not in type_list:
		for k in range(len(index_list)):
			if fribush(str(skills_interest), str(rows[int(index_list[k])]['title'])) == 0:
				pass
			else:
				feedback_list.append(index_list[k])
	return feedback_list

# ----------------------------------------------
# Writing out the final list of classes
# ----------------------------------------------

def final_list(rows, feedback_list):
	url_list = []
	title_list = []
	desc_list = []
#	if len(feedback_list) > 5: 
	for k in range(len(feedback_list)):
		url_list.append(rows[int(feedback_list[k])]['full_url'])
		title_list.append(rows[int(feedback_list[k])]['title'])
		desc_list.append(rows[int(feedback_list[k])]['description'])
#	else:
#		for k in range(len(feedback_list)):
#			url_list.append(rows[int(feedback_list[k])]['full_url'])
#			title_list.append(rows[int(feedback_list[k])]['title'])
#			desc_list.append(rows[int(feedback_list[k])]['description'])
	return url_list, title_list, desc_list

# ----------------------------------------------
# API interacting with database 
# ----------------------------------------------

class Caila(Resource):
#@application.route('/chat_bot/get_course/<type>/<skills_interest>/<result_offset>')
    def get(self, type, skills_interest, result_offset):
	    #conn = e.connect()
	    #result = conn.execute("select * from cailatestdata where type='" + type + "';")
	    result = db.engine.execute("select * from cailatestdata where type= '" + type + "';")
	    rows = result.fetchall()
	    result_offset = int(result_offset)
	    skills_interest = skills_interest.replace("+", " ")
	    print (skills_interest)
	    if len(rows) > 0:
		    i = 0
		    if return_if_nothing(rows, skills_interest, type) == True:
			    jsonresponse = {'messages': [{'text': 'We could not find any ' + type  + ' for ' + skills_interest + '. Please check out other types of content'}]}
		    else:
			    index_list = create_index_list(rows, skills_interest, type)
			    feedback_list = feedback(rows, skills_interest, index_list, type)
			    print(feedback_list)
			    url_list, title_list, desc_list = final_list(rows, feedback_list)
			    try:
				    jsonresponse = {'messages': [
				    {"text": "Title: " + title_list[result_offset]},
				    {"text":"Description: " + desc_list[result_offset]},
				    {"text": url_list[result_offset]}
    #						{
    #							"attachment": {
    #								"type": "web_url",
    #								"payload": {
    #									"url": url_list,
    #									"title": title_list
    #								}
    #							}
    #						}
				    ]}
			    except:
				    jsonresponse = {'messages': [
				    {"text": 'Sorry, there are no more ' + type + ' for ' + skills_interest + '. Check out some of our other content.'}
				    ]}

	    else:
		    jsonresponse = {'messages': [
				    {"text": 'no rows'}
				    ]}
	    return jsonify(jsonresponse)

api.add_resource(Caila, '/chat_bot/get_course/<type>/<string:skills_interest>/<result_offset>')

## ----------------------------------------------
## Run it on the terminal
## ----------------------------------------------

#if __name__ == '__main__':
#	app.run(debug=True)

