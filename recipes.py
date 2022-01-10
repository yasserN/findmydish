import praw
import urllib.request
from praw.models import MoreComments
import re
import pandas as pd
from collections import Counter
import math
WORD = re.compile(r"\w+")
reddit = praw.Reddit(
        client_id = "UEqqzLDufB42jec_Qo4UVQ",
        client_secret = "lOjffzeauPiHSmZtWmUojgvWfHhFCg",
        username = "n0sound",
        password = "chrome123",
        user_agent = "commentTrend"
    )
def trim(s):
  L = s.split("\n")
  return "".join(L)
def get_cosine(vec1, vec2):
    vec1 = text_to_vector(vec1)
    vec2 = text_to_vector(vec2)
    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum([vec1[x] * vec2[x] for x in intersection])

    sum1 = sum([vec1[x] ** 2 for x in list(vec1.keys())])
    sum2 = sum([vec2[x] ** 2 for x in list(vec2.keys())])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)

    if not denominator:
        return 0.0
    else:
        return float(numerator) / denominator


def text_to_vector(text):
    words = WORD.findall(text)
    return Counter(words)



def fetch_recipes():    
    count =0
    post_title = []
    post_url = []
    post_recipe = []
    post_permalink = []
    for submission in reddit.subreddit("recipes").top(limit=1000):
        OP = submission.author
        url = str(submission.url)
        if url.endswith("jpg") or url.endswith("jpeg") or url.endswith("png"):
            for top_level_comment in submission.comments:
                if isinstance(top_level_comment, MoreComments) or top_level_comment.author!=OP:  
                    continue
                comment_text = top_level_comment.body
                if re.findall("(?i)(recipe|ingredients|cup|tbsp|instruction)",trim(comment_text)):
                    post_recipe.append(comment_text)
                    post_title.append(submission.title)
                    post_url.append(url)
                    post_permalink.append(submission.permalink)
                    
                    break
        print(count)
        count+=1
        
    df = pd.DataFrame({"Title":post_title,"URL":post_url,"Recipe":post_recipe,"Permalink":post_permalink})
    df.to_pickle("recipes.pkl")
    
def fetch_food():
    post_recipe = []
    post_title = []
    post_url = []
    post_permalink = []
    i=0
    for submission in reddit.subreddit("food").search('flair_name:"Recipe In Comments"',"top",limit=1000):
        print(i)
        i+=1
        OP = submission.author
        url = str(submission.url)
        if url.endswith("jpg") or url.endswith("jpeg") or url.endswith("png"):
            for top_level_comment in submission.comments:
                if isinstance(top_level_comment, MoreComments):  
                    continue
                comment_text = top_level_comment.body
                if re.findall(r"(?i)(recipe|ingredients|cup|tbsp|instruction)",trim(comment_text)):
                  if top_level_comment.author==OP:
                      post_recipe.append(comment_text)
                      post_title.append(submission.title)
                      post_url.append(url)
                      post_permalink.append(submission.permalink)
                      break
                  else:
                    for second_level_comment in top_level_comment.replies:
                      if isinstance(second_level_comment, MoreComments):  
                        continue
                      if second_level_comment.author==OP and re.match(r"(?i)(recipe|ingredients|cup|tbsp|instruction)",trim(second_level_comment.body)):
                        post_recipe.append(second_level_comment.body)
                        post_title.append(submission.title)
                        post_url.append(url)
                        post_permalink.append(submission.permalink)
                        break
                    break

    df = pd.DataFrame({"Title":post_title,"URL":post_url,"Recipe":post_recipe,"Permalink":post_permalink})
    df.to_pickle("food.pkl")
def join_files():
    df1 = pd.read_pickle("recipes.pkl")
    df2 = pd.read_pickle("food.pkl")
    df = pd.concat([df1,df2])
    df.to_pickle("all.pkl")
    return
    
def ing(L):
    df = pd.read_pickle('all.pkl')
    index_to_cosine = {}
    for i in range(1,len(df)):
        recipe  = df.iloc[i]['Recipe']
        how_similar = 0
        for ingredient in L:
            if get_cosine(ingredient,recipe) == 0:
                how_similar = 0
                break           
            how_similar += get_cosine(ingredient,recipe)
        index_to_cosine[i] = how_similar/len(L)
    
    index_to_cosine = sorted(index_to_cosine.items(), key=lambda x: x[1], reverse=True)
    if index_to_cosine[0][1]==0:
        return "No recipe matching ingredients found"
    print(index_to_cosine[0][0])
    return df.iloc[index_to_cosine[0][0]]['Title']
            

join_files()