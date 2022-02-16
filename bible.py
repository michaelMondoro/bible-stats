import json
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity,cosine_distances
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

stopwords = list(stopwords.words("english"))
stopwords += ['.','?',',',':','"',"'"]

f = open('catholicbible.json')
bible = json.load(f)
bible.pop('charset')
books = list(bible.keys())


def get_bible():
    return bible

def get_books():
    return books

def get_chapters(book):
    return list(bible[book].keys())

def chapter_count():
    l = 0
    for book in books:
        l += len(bible[book].keys())
    return l

def verse_count():
    l = 0
    for book in books:
        for chapter in bible[book]:
            l += len(bible[book][chapter].keys())
    return l

# TODO: Fix search to allow for phrases as well
def search_book(query, book):
    count = 0
    appearances = []
    book_contents = bible.get(book)

    for chapter in book_contents:
        chapter_content = book_contents.get(chapter)
        
        for verse in chapter_content:
            verse_content = chapter_content.get(verse)
            if re.findall(f"\s{query}[!@#$%^&*(),\s]",verse_content.lower()): #query in verse_content.lower():
                count += 1
                appearances.append((chapter, verse))
    
    # print(f"[{query}] appears {count} times in {book}")
    # print(f"\n{appearances}\n")
    return appearances


def search_bible(query):
    total_appearances = {}
    count = 0
    for b in books:
        data = search_book(query, b)
        total_appearances[b] = data
        count += len(data)
    return (count, total_appearances)
    # print(f"[{query}] appears {count} times in the Bible")

# Return Bible book as list of verses
def get_book(book):
    # Json data
    book_json = bible.get(book)
    content = []
    verses_per_chapter = []
    for chapter in book_json:
        chapter = book_json[chapter]
        verses_per_chapter.append(len(chapter))
        for verse in chapter:
            content.append(f" {chapter[verse]}")
    
    return content, verses_per_chapter


def get_chapter_verse(i,verse_counts):
    total = 0
    for j,count in enumerate(verse_counts):
        total += count
        if i <= total:
            return j+1,count-(total-i)+1
        

def remove_stopwords(data):
    new_data = []
    for sent in data:
        sent = word_tokenize(sent)
        new_sent = ""
        for word in sent:
            if word not in stopwords:
                new_sent += word + " "
        new_data.append(new_sent)
    return new_data



def semantic_search(book, query, model, vocab):
    # Load book data
    book_data, verse_counts = get_book(book)

    # get query vector and search based on cosine similarity of all verses
    query_vec = model.transform([query])
    similar = []
    for i,verse_data in enumerate(book_data):
        verse_data = model.transform([verse_data])
        similarity = cosine_similarity(query_vec,verse_data)
        if similarity > .15:
            chapter,verse = get_chapter_verse(i, verse_counts)
            similar.append((chapter,verse,round(float(similarity),2),book_data[i]))


    similar.sort(key=lambda x:x[2],reverse=True)
    return similar
# # Print results
# for verse in similar:
#     print(f"\nChapter {verse[0]} Verse {verse[1]} Score: {verse[2]:.4}:\n {data[verse[3]]}")



def build_word_model():
    # Load book data
    data = []

    for book in bible:
        for chapter in bible[book]:
            chapter_data = ""
            for verse in bible[book][chapter]:
                chapter_data += f" {bible[book][chapter][verse]}"
            
            data.append(chapter_data)  


    # Remove stopwords and punctuation
    clean_data = remove_stopwords(data)


    # Create vectorizer and generate vocabulary
    tfidf = TfidfVectorizer()
    vocab = tfidf.fit_transform(clean_data)

    num_to_word = {}
    for token in tfidf.vocabulary_:
        num = tfidf.vocabulary_[token]
        num_to_word[num] = token
    
    return tfidf, vocab, num_to_word

if __name__ == "__main__":
    
    model,vocab,num_word = build_word_model()
    results = semantic_search('John','the light of the world',model,vocab)
    print(results)
