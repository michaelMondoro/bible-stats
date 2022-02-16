from flask import Flask, redirect, render_template, request, url_for
from bible import *
import json

app = Flask(__name__)
model,vocab,num_word = build_word_model()

@app.route('/', methods=["GET","POST"])
def index():
    books = get_books()
    if request.method == "GET":
        return render_template('index.html', books=books, num_words=vocab.shape[1])
        

@app.route('/semantic', methods=["GET","POST"])
def semantic():
    books = get_books()
    err = None
    results = []
    if request.method == "GET":
        return render_template('semantic.html', results=results,books=books,err=None)

    book = request.form.get('book')
    query = request.form.get('query')
    books = get_books()
    if book and query:
        results = semantic_search(book, query, model, vocab)
    else:
        err = True
    
    return render_template('semantic.html', results=results,books=books,err=err)


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
        return render_template('word.html', word_query=word_query, word_results=word_results, books=books, err=None)

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

    return render_template('word.html', word_query=word_query,total=total,titles=labels,counts=counts,verses=verses, books=books, err=err)


@app.route('/results',methods=["POST","GET"])
def book():
    data = {}
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
    print(f"VALUES: {values}")
    for value in values:
        q = value.split(' ')
        chap, verse = q[1],q[3]
        data[value] = [chap,verse,""]
        chapter_content = book[chap]
        for v in chapter_content:
            data[value][2] += f" [{v}] {chapter_content[v]}"

        chapters.append(chap)
        verses.append(verse)
        
        
        

    
    return render_template('book.html',values=values,data=data,query=query,chapters=chapters,title=book_title)



if __name__=='__main__':
    app.run(debug=True)
