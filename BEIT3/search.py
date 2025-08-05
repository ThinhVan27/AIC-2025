from pymongo import MongoClient

uri = "mongodb+srv://EEIoT_newbie:ILOVEAIFOREVER@cluster0.xolr95j.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri)

db = client['EEIoT_newbie']
collection = db['frames']

pipeline = [
    {
        "$search": {
            "index": "default",
            "compound": {
                "must": [
                    {
                        "text": {
                            "query": "a3green",       # từ khóa tìm
                            "path": "detection",         # trường muốn search
                            "fuzzy": {
                                "maxEdits": 1,      # số ký tự có thể sai
                                "prefixLength": 2  # số ký tự đầu tiên phải đúng
                            }
                        }
                    },
                    # {
                    #     "text": {
                    #         "query": "Baber shop",  # từ khóa tìm
                    #         "path": "text",         # trường muốn search
                    #         "fuzzy": {
                    #             "maxEdits": 1,      # số ký tự có thể sai
                    #             "prefixLength": 2  # số ký tự đầu tiên phải đúng
                    #         }
                    #     }
                    # }
                ],
                # "should":[
                #     {
                #         "text": {
                #             "query": ["e1car e2car", "a4yellow"],       # từ khóa tìm
                #             "path": "detection",         # trường muốn search
                #             "fuzzy": {
                #                 "maxEdits": 1,      # số ký tự có thể sai
                #                 "prefixLength": 2  # số ký tự đầu tiên phải đúng
                #             }
                #         }
                #     },
                #     {
                #         "text": {
                #             "query": ["Baber shop", "Car wash"],  # từ khóa tìm
                #             "path": "text",         # trường muốn search
                #             "fuzzy": {
                #                 "maxEdits": 1,      # số ký tự có thể sai
                #                 "prefixLength": 2  # số ký tự đầu tiên phải đúng
                #             }
                #         }
                #     }
                # ]
            }
        }
    },
    {    "$project": {
            "_id": 0,
            "path": 1,
            "detection": 1,
            "text": 1,
            "score": {"$meta": "searchScore"}
        }
    },
    {
        "$limit": 5
    }
]
if __name__ == "__main__":
    results = collection.aggregate(pipeline)
    for doc in results:
        print(doc)