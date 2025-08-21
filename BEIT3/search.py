from pymongo import MongoClient
import time
import save_data


uri = "mongodb+srv://EEIoT_newbie:ILOVEAIFOREVER@cluster0.xolr95j.mongodb.net/"
client = MongoClient(uri,  serverSelectionTimeoutMS=60000)

db = client['EEIoT_newbie']
collection = db['frames']

beit3 = create_beit3()
clip, tokenizer, preprocess = create_clip()

pipeline = [
    {
        "$search": {
            "index": "default",
            "compound": {
                "must": [
                    {
                        "compound": {
                            "must": [
                                {
                                    "text":{
                                        
                                    }
                                },
                                {
                                  
                                }
                            ]
                        },
                        "compound": {
                            "should": [
                                
                            ]
                        }
                    },
                    {
                        "text": {
                            "query": "hóa",
                            "path": "text",
                            "fuzzy": {
                                "maxEdits": 1,
                                "prefixLength": 2
                            }
                        }
                    }
                ]
            }
            
        }
    },
    {
        "$limit": 2000
    },
    {    "$project": {
            "_id": 0,
            "idx": 1,
            "path": 1,
        }
    }
]

def create_fuzzy_query(detection=None, objects=None, text=None):
    od_query = []
    if objects:
        od_query.append({
            "text": {
                "query": objects,
                "path": "objects",
                "fuzzy": {
                    "maxEdits": 1,
                    "prefixLength": 2
                }
            }
        })
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
    return od_query, text_query

def fuzzy_search(collection, detection=None, objects=None, operator="AND", text=None, k=100):
    od_query, text_query = create_fuzzy_query(detection, objects, text)
    if od_query == [] and text_query==None:
        return []
    
    pipeline = [
    {
        "$search": {
            "index": "default",
            "compound": {
                "must": [
                    {
                        "compound": {
                            "must": od_query if operator == "AND" else []
                        },
                        "compound": {
                            "should": od_query if operator != "AND" else []
                        }
                    }
                ]
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

def search(collection, metadata, query1=None, index=None, model_name='beit3', augment=False, k=100, query2=None, detection=None, objects=None, operator="AND", text=None):
    topk = None
    frame_paths = []
    
    topk_faiss = retrieve(query1, index, augment, k, query2, model=beit3 if model_name=="beit3" else (clip, tokenizer, preprocess))
    
    topk_fuzzy = fuzzy_search()
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
                reranking.append(1/(1000+i)+1/(1000+maping[idx]))
            else:
                reranking.append(1/(1000+i))
        
        topk = sorted(zip(topk_faiss, reranking), key=lambda x: x[1], reverse=True)
        topk = [idx for idx, _ in topk]
    if topk:
        frame_paths = [metadata[idx] for idx in topk]
    return frame_paths

def temporal_search(metadata, frame_idx=-1):
    frame_paths = []
    for idx in range(min(frame_idx-10, 0), max(frame_idx+10, len(metadata))):
        frame_paths.append(metadata[idx]['idx'])
    return frame_paths

if __name__ == "__main__":
    s = time.time()
    results = collection.aggregate(pipeline)
    e = time.time()
    
    for doc in results:
        print(doc)
    print(float(e-s))
