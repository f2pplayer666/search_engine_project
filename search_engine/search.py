import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer     #TF-IDF this class is used to convert text documents into TF-IDF numerical vectors.
from sklearn.metrics.pairwise import cosine_similarity          #cosine_similarity function measures similarity between two vectors using cosine distance.

#LOAD PRESET
df=pd.read_csv("data/documents.csv")     #it will load the contents from documents.csv file

#combine text fields
documents=df["content"].astype(str).tolist()      #access contentn columns from dataframe converts them to string and then converts column into python list

#initialize TF-IDf
vectorizer=TfidfVectorizer(stop_words="english")         #ignore common english words
tfidf_matrix=vectorizer.fit_transform(documents)        #learns vocabulary from docs then converts each doc into tf-idf vector then that res is a main matrix where each row represents a matrix

def ranked_search(query,top_k=5):       #top_k=5 -> max no.of res to return it is 5
    if not query.strip():
        return []       #return empty list
    
#CONVERT QUERY TO TF-IDF VECTOR
    query_vector=vectorizer.transform([query])
    
#COMPUTE COSINE_SIMILARITY
    similarity_scores=cosine_similarity(query_vector,tfidf_matrix)[0]       #res is 2D array with one row the [0] extracts 1st row as a 1D array of similar scores
   
   #GET TOP RESULTS
    ranked_indices=similarity_scores.argsort()[::-1][:top_k]
   
    results=[]
    for idx in ranked_indices:
        if similarity_scores[idx]>0:                        #Accesses the row at position idx using .iloc
            results.append({
                "id":int(df.iloc[idx]["id"]),
                "title":df.iloc[idx]["title"],
                "content":df.iloc[idx]["content"],
                "score":float(similarity_scores[idx])
            }) 
            
    return results        