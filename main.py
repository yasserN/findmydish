from tkinter import *
from PIL import ImageTk, Image,ImageOps
import re
import pandas as pd
from collections import Counter
import math
import requests
import json
root = Tk()

i=2
WORD = re.compile(r"\w+")
current_dish = 0


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
    return df.iloc[index_to_cosine[0][0]]['Title']
            

def addIng():
    global i
    if i==1:
        ing2.grid()
        ing2_text.grid(row=2,column=1)
        i+=1
    elif i==2:
        ing3.grid()
        ing3_text.grid(row=3,column=1)
        i+=1
        
    elif i==3:
        ing4.grid()
        ing4_text.grid(row=4,column=1)
        i+=1
    elif i==4:
        ing5.grid()
        ing5_text.grid(row=5,column=1)
        i+=1
    if i==5:
        return
        
def updateImage(image1):
    image1 = image1.resize((350, 350), Image.ANTIALIAS)
    border = (2, 2,2, 2)
    image1 = ImageOps.expand(image1, border=border, fill="black")
    test = ImageTk.PhotoImage(image1)
    pic = Label(image=test)
    pic.image = test
    pic.place(x=460,y=100)

        


def removeIng():
    global i
    
    if i==1:
        return
    if i==2:
        ing2.grid_forget()
        ing2_text.grid_forget()
        ing2_text.delete(0, "end")
        i-=1
    elif i==3:
        ing3.grid_forget()
        ing3_text.grid_forget()
        ing3_text.delete(0, "end")
        i-=1
    elif i==4:
        ing4.grid_forget()
        ing4_text.grid_forget()
        ing4_text.delete(0, "end")
        i-=1
    elif i==5:
        ing5.grid_forget()
        ing5_text.delete(0, "end")
        ing5_text.grid_forget()
        i-=1



def search_fxn():
    prev_rec['state'] = 'disabled'
    t1 = ing1_text.get()
    t2 = ing2_text.get()
    t3 = ing3_text.get()
    t4 = ing4_text.get()
    t5 = ing5_text.get()
    L = [t1,t2,t3,t4,t5]
    L = [t for t in L if t!=""]
    if len(L)==0:
        return
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
        dish_name.config(text= "No recipe matching ingredients found")
        ima = Image.open("notfound.png")
        next_rec['state'] = 'disabled'
        updateImage(ima)
        return
    
    with open('data.json', 'w') as fp:
        json.dump(index_to_cosine, fp)
    dish_index = index_to_cosine[0][0]
    dish_text = df.iloc[dish_index]['Title']
    if(index_to_cosine[1][1]==0):
        next_rec['state'] = 'disabled'
    else:
        next_rec['state'] = 'active'
        
    URL = df.iloc[dish_index]['URL']
    recipe_text = df.iloc[dish_index]['Recipe']
    perma_text = df.iloc[dish_index]['Permalink']
    url_text.delete("1.0","end")
    perma_text = "https://www.reddit.com" + perma_text
    url_text.insert(END,perma_text)
    im = Image.open(requests.get(URL, stream=True).raw)
    updateImage(im)
    dish_name.config(text=dish_text)
    recipe_box.delete("1.0", "end")
    recipe_box.insert(END,recipe_text)
def updateNext():
    global current_dish
    current_dish+=1
    df = pd.read_pickle('all.pkl')
    with open('data.json', 'r') as fp:
        index_to_cosine = json.load(fp)
    if(index_to_cosine[current_dish+1][1]==0):
        next_rec['state'] = 'disabled'
    if(current_dish>=0):
        prev_rec['state'] = 'active'
        
    
   
    dish_index = index_to_cosine[current_dish][0]
    dish_text = df.iloc[dish_index]['Title']
    URL = df.iloc[dish_index]['URL']
    recipe_text = df.iloc[dish_index]['Recipe']
    perma_text = df.iloc[dish_index]['Permalink']
    url_text.delete("1.0","end")
    perma_text = "https://www.reddit.com" + perma_text
    url_text.insert(END,perma_text)
    im = Image.open(requests.get(URL, stream=True).raw)
    updateImage(im)
    dish_name.config(text=dish_text)
    recipe_box.delete("1.0", "end")
    recipe_box.insert(END,recipe_text)
    


    

def updatePrev():
    next_rec['state'] = 'active'
    global current_dish
    current_dish-=1
    df = pd.read_pickle('all.pkl')
    with open('data.json', 'r') as fp:
        index_to_cosine = json.load(fp)
    if(current_dish==0):
        prev_rec['state'] = 'disabled'

    
   
    dish_index = index_to_cosine[current_dish][0]
    dish_text = df.iloc[dish_index]['Title']
    URL = df.iloc[dish_index]['URL']
    recipe_text = df.iloc[dish_index]['Recipe']
    perma_text = df.iloc[dish_index]['Permalink']
    url_text.delete("1.0","end")
    perma_text = "https://www.reddit.com" + perma_text
    url_text.insert(END,perma_text)
    im = Image.open(requests.get(URL, stream=True).raw)
    updateImage(im)
    dish_name.config(text=dish_text)
    recipe_box.delete("1.0", "end")
    recipe_box.insert(END,recipe_text)
    
    
    
    

df = pd.read_pickle("all.pkl")
ing1 = Label(root,text="Ingredient 1")
ing1.grid(row=1,column=0)
ing1_text = Entry(root)
ing1_text.grid(row=1,column=1)
ing1.config(font=("Bahnschrift SemiBold", 11))


ing2 = Label(root,text="Ingredient 2")
ing2.grid(row=2,column=0)
ing2_text = Entry(root)
ing2_text.grid(row=2,column=1)
ing2.config(font=("Bahnschrift SemiBold", 11))

ing3 = Label(root,text="Ingredient 3")
ing3.grid(row=3,column=0)
ing3_text = Entry(root)
ing3_text.grid(row=3,column=1)
ing3.grid_forget()
ing3_text.grid_forget()
ing3.config(font=("Bahnschrift SemiBold", 11))


ing4 = Label(root,text="Ingredient 4")
ing4.grid(row=4,column=0)
ing4_text = Entry(root)
ing4_text.grid(row=4,column=1)
ing4.grid_forget()
ing4_text.grid_forget()
ing4.config(font=("Bahnschrift SemiBold", 11))

ing5 = Label(root,text="Ingredient 5")
ing5.grid(row=5,column=0)
ing5_text = Entry(root)
ing5_text.grid(row=5,column=1)
ing5.grid_forget()
ing5_text.grid_forget()
ing5.config(font=("Bahnschrift SemiBold", 11))




add_ing = Button(root,text="+",padx=5,pady=5,command= addIng)
add_ing.grid(row=0,column=0)
remove_ing = Button(root,text="-",padx=5,pady=5,command=removeIng)
remove_ing.grid(row=0,column=1)
prev_rec = Button(root,text="<",padx=8,pady=8,command=updatePrev)
prev_rec.place(x=100,y=300)
next_rec = Button(root,text=">",padx=8,pady=8,command=updateNext)
next_rec.place(x=320,y=300)

search = Button(root,text="Search",padx=5,pady=5,command=search_fxn)
search.place(x=320,y=0)

prev_label = Label(root,text="Previous Recommendation")
prev_label.place(x=20,y=280)
prev_label.config(font=("Bahnschrift SemiBold", 9))


next_label = Label(root,text="Next Recommendation")
next_label.place(x=240,y=350)
next_label.config(font=("Bahnschrift SemiBold", 9))


url_label = Label(root,text="Post URL")
url_label.config(font=("Bahnschrift SemiBold", 9))
url_text = Text(root,height=1,width=25)
url_label.place(x=20,y=435)
url_text.place(x=110,y=435)
url_text.config(font=("Consolas", 9))



image1 = Image.open("empty.png")
image1 = image1.resize((350, 350), Image.ANTIALIAS)
border = (2, 2,2, 2)
image1 = ImageOps.expand(image1, border=border, fill="black")
test = ImageTk.PhotoImage(image1)
pic = Label(image=test)
pic.image = test
pic.place(x=460,y=100)

recommend = Label(root,text="Recommended Dish:")
recommend.place(x=460,y=0)
recommend.config(font=("Bahnschrift SemiBold", 13))
dish_name = Label(root,text="",wraplength=360)
dish_name.config(font=("Bahnschrift Light", 12))
dish_name.place(x=460,y=35)


recipe_label = Label(root,text="Recipe:")
recipe_label.place(x=15,y=520)
recipe_label.config(font=("Bahnschrift SemiBold", 15))
recipe_box = Text(root, height = 8, width = 66)
recipe_box.config(font=("Bahnschrift Light", 11))
recipe_box.place(x=15,y=570)




root.geometry("900x800")
root.mainloop()


# disable next and before buttons when recommendations are done (trim zero values out of cosine array)