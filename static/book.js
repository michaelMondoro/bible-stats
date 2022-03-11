const book = document.querySelector('.book');
var results = document.querySelectorAll('.result');

book.addEventListener('change', (event) => {
    for (const result of results.entries()) {
        rresult = result[1];
        rresult.style.display = "none";
    }
    var elmnt = document.getElementById(`${book.value}`);
    elmnt.style.display = 'inline-block';
});