from models import *
from utils import *
from transformers import XLMRobertaTokenizer
import faiss
import numpy as np
import json
import os
import torch
from pymongo import MongoClient

def retrieve(query1, index, k, augment=False, query2=None, query3=None, model=None, device='cpu', llm=None):
	sims1, ids1 = faiss_search_results(query1, index, k, augment, model, device, llm)
	topk_ids1, topk_sims1 = topk_fusion(sims1, ids1)
 
 
	if query2 is not None:
		sims2, ids2 = faiss_search_results(query2, index, k, augment, model, device, llm)
		topk_ids2, topk_sims2 = topk_fusion(sims2, ids2)

		topk_ids3, topk_sims3 = [], []
		if query3 is not None:
			sims3, ids3 = faiss_search_results(query3, index, k, augment, model, device, llm)
			topk_ids3, topk_sims3 = topk_fusion(sims3, ids3)

		reranking = []
		map2= dict(zip(topk_ids2, range(k)))
		map3= dict(zip(topk_ids3, range(k)))
		
		set_ids2 = set(topk_ids2)
		set_ids3 = set(topk_ids3)
		
		for i, idx1 in enumerate(topk_ids1):
			max_sim = 0
			for offset in range(10):
				temp_sim1 = topk_sims1[i]
				if idx1 + offset in set_ids2:
					temp_sim1 += (topk_sims2[map2[idx1+offset]]) # 1/(60+map[idx1+offset])

					temp_sim2 = 0
					if query3 is not None:
						for offset2 in range(10):
							if idx1+offset+offset2 in set_ids3:
								temp_sim2 = max(temp_sim2, topk_sims3[map3[idx1+offset+offset2]])
					temp_sim1 += temp_sim2

	 
				max_sim = max(max_sim, temp_sim1)
			reranking.append(max_sim)

		map = list(zip(topk_ids1, reranking))
		zip_sorted= list(sorted(map, key=lambda x: x[1], reverse=True))
  
		topk_ids1, _ = zip(*zip_sorted)

	return topk_ids1

def create_fuzzy_query(detection=None, objects=None, text=None):
	ob_query = []
	if objects:
		ob_query.append({
			"text": {
				"query": objects,
				"path": "objects",
				"fuzzy": {
					"maxEdits": 1,
					"prefixLength": 2
				}
			}
		})
	od_query = []
	if detection:
		for bb in detection:
			od_query.append({
				"text": {
					"query": bb,
					"path": "detection",
					"fuzzy": {
						"maxEdits": 1,
						"prefixLength": 2
					}
				}
			})
	text_query = None       
	if text:
		text_query = {
			"text": {
				"query": text,
				"path": "text",
				"fuzzy": {
					"maxEdits": 1,
					"prefixLength": 2
				}
			}
		}
	return ob_query, od_query, text_query

def fuzzy_search(collection, detection=None, objects=None, operator="AND", text=None, k=100):
	if collection is None:
		return []
	
	ob_query, od_query, text_query = create_fuzzy_query(detection, objects, text)
	if ob_query == [] and od_query == [] and text_query==None:
		return []
	
	if od_query == []:
		od_clause = []
	else:
		od_clause = [{
			"compound": {
				"must": od_query
			}
		}] if operator == "AND" else [{
				"compound": {
					"should": od_query
				}
			}]
	clause = [] if ob_query == [] and od_query == [] else [
					{
						"compound": {
							"must": ob_query + od_clause
						}
					}]
	pipeline = [
	{
		"$search": {
			"index": "default",
			"compound": {
				"must": clause
			}
			
		}
	},
	{
		"$limit": k
	},
	{    "$project": {
			"_id": 0,
			"idx": 1,
		}
	}
	]
	if text:
		pipeline[0]["$search"]["compound"]["must"].append(text_query)
	
	results = collection.aggregate(pipeline)
	
	return [res['idx'] for res in results]

def search(collection, 
		   metadata, 
		   model=None, 
		   query1=None, 
		   index=None, 
		   augment=False, 
		   k=100, 
		   query2=None,
		   query3=None, 
		   llm=None, 
		   detection=None, 
		   objects=None, 
		   operator="AND", 
		   text=None, 
		   device='cpu'):
	
	topk = None
	topk_faiss = []
	frame_paths = []
	topk_fuzzy = []
	
	if query1 is not None:
		topk_faiss = retrieve(query1, index, k, augment, query2, query3, model, device, llm)
	
	topk_fuzzy = fuzzy_search(collection, detection, objects, operator, text, k)

	if topk_fuzzy == []:
		topk = topk_faiss
	elif topk_faiss == []:
		topk = topk_fuzzy
	else:
		maping = dict(zip(topk_fuzzy, range(k)))
		idx_set = set(topk_fuzzy)
		
		reranking = []
		for i, idx in enumerate(topk_faiss):
			if idx in idx_set:
				reranking.append(1/(100+i)+1/(100+maping[idx]))
			else:
				reranking.append(1/(100+i))
		
		topk = sorted(zip(topk_faiss, reranking), key=lambda x: x[1], reverse=True)
		topk = [idx for idx, _ in topk]
	if topk:
		frame_paths = [metadata[idx] for idx in topk]
	else:
		topk = []
	return topk, frame_paths

def temporal_search(metadata, frame_idx):
	neighbor_frames = []
	lower_bound = max(0, frame_idx-10)
	upper_bound = min(frame_idx+11, len(metadata))
 
	neighbor_frames.extend(metadata[lower_bound:upper_bound])

if __name__ == "__main__":
	# device = 'cuda' if torch.cuda.is_available() else 'cpu'
	device = 'cpu'
	
	uri = "mongodb+srv://EEIoT_newbie:ILOVEAIFOREVER@cluster0.xolr95j.mongodb.net/"
	client = MongoClient(uri,  serverSelectionTimeoutMS=60000)

	db = client['EEIoT_newbie']
	collection = db['frames']

	# Create models
	beit3, beit3_tokenizer, index1 = None, None, None
	# beit3, beit3_tokenizer = create_beit3()
	clip, clip_tokenizer, preprocess = create_clip()
	llm = create_llm()
	
	# index1, metadata = create_faiss_index('embedding-info', 'metadata', model='beit3', get_metadata=True)
	index2, metadata = create_faiss_index('embedding-info', 'metadata', model='clip', get_metadata=True)

	while True:
		query1 = input("Enter your query: ")
		if query1 == "exit":
			break
		query1 = query1 if query1 else None
		
		detection = input("Enter detection keywords (comma separated) or leave blank: ")
		detection = detection.split(",") if detection else None
		
		objects = input("Enter object keywords (comma separated) or leave blank: ")
		objects = objects if objects else None
		
		text = input("Enter text keywords or leave blank: ")
		text = text if text else None
		
		model_name = input("Enter model (beit3/clip: 0/1): ")
		model = (beit3, beit3_tokenizer) if model_name == "0" else (clip, clip_tokenizer, preprocess)
		
		index = index1 if model_name == "0" else index2
		
		k = input("Enter k: ")
		k = int(k) if k else 100
		
		query2 = input("Enter your query: ")
		if query2 == "exit":
			break
		query2 = query2 if query2 else None
		
		query3 = input("Enter your query: ")
		if query3 == "exit":
			break
		query3 = query3 if query3 else None
		
		operator = input("Enter Operator: ")
		operator = "AND" if operator=="0" else "OR"
		
		augment = input("Enter Augment: ")
		augment = True if augment == "1" else False
		if augment:
			llm_ = llm
		else:
			llm_ = None
		
		topk, frame_paths = search(collection=collection,
									metadata=metadata, 
									model=model, # [0, 1]
									query1=query1, # ""
									index=index,
									augment=augment, # [0, 1]
									k=k, # int
									query2=query2, # text ""
									query3=query3,
									llm=llm_,
									detection=detection, # ["a1car", "e1person", "h5tree", ...]
									objects=objects, # "car1 car2 person1 person2"
									operator=operator, # [0, 1] = ["AND", "OR"]
									text=text,
									device=device)  # text ""
	
		# for idx in topk:
		#     print(metadata[idx])
		
		print(frame_paths)

		# ["keyframes/L12/frame_0011.jpg", url, url, ....]