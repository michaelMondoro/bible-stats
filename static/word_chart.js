    
function chart(query){
    Chart.defaults.font.size = 16;
    Chart.defaults.elements.bar.borderWidth = 2;

    var results = document.querySelectorAll('.meta');
    var books = [];
    var counts = [];
    var verses = [];

    for (const result of results.entries()){
        rresult = result[1];
        books = books.concat(rresult.getAttribute('book'));
        counts = counts.concat(rresult.getAttribute('count'));
        verses = verses.concat( [rresult.getAttribute('value').match(/[\w ]*/g) ]);
        for (let i = 0; i<verses.length; i++) {
            for (let j = 0; j<verses[i].length; j++){
                if (verses[i][j].length < 2) {
                    verses[i].splice(j,1);
                }
            }
        }
    }


    const data = {
        click: function(e){
            alert("click");
        },
        labels: books,
        datasets: [{
        label: query,
        backgroundColor: 'rgba(135, 206, 250,.4)',
        borderColor: 'rgba(0, 100, 200,.5)',
        data: counts,
        }]
    };
    const config = {
        type: 'bar',
        data: data,
        options: {
            onClick: (event, activeElements) => {
            if(activeElements.length > 0){
                var indx = activeElements[0].index;
                var val = books[indx];
            
                document.location.href = `results?book=${val}&values=${verses[indx]}&search_query=${word_query}`;
            }
            
        },
            
        },
    };

    const myChart = new Chart(
        document.getElementById('myChart'),
        config
    );
}