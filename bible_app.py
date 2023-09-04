from flask import Flask, redirect, render_template, request, url_for
from bible import *
import pickle

app = Flask(__name__)
# model,vocab,num_word = build_word_model()
model = pickle.load(open("model.pickle",'rb'))
vocab = pickle.load(open("vocab.pickle",'rb'))


@app.route('/', methods=["GET","POST"])
def index():
    books = get_books()
    if request.method == "GET":
        return render_template('index.html', books=books, num_words=vocab.shape[1],num_chaps="{:,}".format(chapter_count()),num_verses="{:,}".format(verse_count()))
        

@app.route('/semantic', methods=["GET","POST"])
def semantic():
    books = get_books()
    err = None
    results = []
    if request.method == "GET":
        return render_template('semantic.html', results=results,books=books,err=None,num_words=vocab.shape[1],num_chaps="{:,}".format(chapter_count()),num_verses="{:,}".format(verse_count()))

    book = request.form.get('book')
    query = request.form.get('query')
    books = get_books()
    if book and query:
        results = semantic_search(book, query, model, vocab)
    else:
        err = True
    
    return render_template('semantic.html', results=results,books=books,err=err,num_words=vocab.shape[1],num_chaps="{:,}".format(chapter_count()),num_verses="{:,}".format(verse_count()))


@app.route('/word', methods=["GET","POST"])
def word():
    books = get_books()
    err = None
    word_query = request.form.get('word_query')
    word_results = []
    verses = []
    labels = []
    counts = []
    total = 0

    if request.method == "GET":
        return render_template('word.html', word_query=word_query, word_results=word_results, books=books, err=None,num_words=vocab.shape[1],num_chaps="{:,}".format(chapter_count()),num_verses="{:,}".format(verse_count()))

    if word_query:
            word_results = search_bible(word_query)
    else: 
        err=True

    if len(word_results) > 0:
        appearances = word_results[1]
        total = word_results[0]
        for book in appearances:
            if len(appearances[book]) > 0:
                labels.append(book)
                counts.append(len(appearances[book]))
                verses.append([f"Chapter {x[0]} Verse {x[1]}" for x in appearances[book]])

    return render_template('word.html', word_query=word_query,total=total,titles=labels,counts=counts,verses=verses, books=books, err=err,num_words=vocab.shape[1],num_chaps="{:,}".format(chapter_count()),num_verses="{:,}".format(verse_count()))


@app.route('/results',methods=["POST","GET"])
def book():
    data = {}
    chap_data = {}
    bible = get_bible()
    book_title = request.args.get('book')
    values = request.args.get('values')
    query = request.args.get('search_query')

    if values:
        values = [ x for x in values.split(',') if len(x) > 0]

    books = get_books()
    if not book_title or book_title not in books:
        return redirect(url_for('book',book='Genesis'))

    book = bible.get(book_title)
    chapters = []
    verses = []

    # Build chapter/verse dictionary
    for value in values:
        q = value.split(' ')
        chap, verse = q[1],q[3]
        if chap in chap_data.keys():
            chap_data[chap].append(verse)
        else:
            chap_data[chap] = [verse]

    # Build chapter strings
    for chap in chap_data:
        data[chap] = []
        chapter_content = book[chap]
        for v in chapter_content:
            if str(v) in chap_data[chap]:
                data[chap] += [(v, chapter_content[v], 1)]
            else:
                data[chap] += [(v, chapter_content[v], 0)]

        chapters.append(chap)
        verses.append(verse)
        
        
        

    print(chap_data)
    print(data)
    return render_template('book.html',values=values,verses=verses,data=data,query=query,chapters=chapters,title=book_title,num_words=vocab.shape[1],num_chaps="{:,}".format(chapter_count()),num_verses="{:,}".format(verse_count()))

@app.errorhandler(404)
def not_found(e):
    return "<h1>404 NOT FOUND</h1>"

if __name__=='__main__':
    app.run()
