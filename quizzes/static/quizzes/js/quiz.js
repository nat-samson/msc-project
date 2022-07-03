const question = document.getElementById("question-header");
const options = Array.from(document.getElementsByClassName("option-detail"));
const button = document.getElementById("continue")

// TODO: replace with data from settings
// TODO: ensure document is ready
const CORRECT_ANSWER_PTS = 10;
const INCORRECT_ANSWER_PTS = -2;

let currentQuestion = {};
let score = 0;
let questionCounter = 0;
let results = {};
let availableQuestions = [];
let allowUserAnswer = false;

// dummy questions
// TODO: replace with a Jquery call
let questions = [
    {
        'word_id': 3,
        'origin_to_target': true,
        'word': 'Mouse',
        'correct_answer': 0,
        'options': ['Die Maus', 'Der Bär', 'Der Hund', 'Die Katze']
    },
    {
        'word_id': 2,
        'origin_to_target': true,
        'word': 'Dog',
        'correct_answer': 1,
        'options': ['Die Maus', 'Der Hund', 'Die Katze', 'Der Bär']
    },
    {
        'word_id': 1,
        'origin_to_target': false,
        'word': 'Die Katze',
        'correct_answer': 1,
        'options': ['Dog', 'Cat', 'Bear', 'Mouse']
    },
    {
        'word_id': 7,
        'origin_to_target': false,
        'word': 'Der Fisch',
        'correct_answer': 3,
        'options': ['Cat', 'Mouse', 'Bear', 'Fish']
    }
]

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');

startQuiz = () => {
    availableQuestions = [... questions];
    getNextQuestion();
};

getNextQuestion = () => {
    if(availableQuestions.length === 0) {
        console.log(results);
        return;
    }
    button.style.display = "none";
    questionCounter++;

    // question order is shuffled on the client side
    let questionIndex = Math.floor(Math.random() * availableQuestions.length);
    currentQuestion = availableQuestions[questionIndex];

    // update the question in the DOM
    if(currentQuestion.origin_to_target) {
        console.log('English to German!')
    }
    question.firstElementChild.innerText = currentQuestion.origin_to_target
    question.lastElementChild.innerText = currentQuestion.word;

    options.forEach(option => {
            const optionNum = option.dataset['num'];
            option.innerText = currentQuestion['options'][optionNum];
        }
    )
    availableQuestions.splice(questionIndex, 1);

    allowUserAnswer = true;
};

resetState = () => {
    options.forEach(option => {
        option.parentElement.classList.remove('correct', 'incorrect');
    })
}

submitResults = () => {
    $.ajax({
        type: "POST",
        headers: {'X-CSRFToken': csrftoken},
        dataType: "json",
        data: results,
        success: function (data) {
            // any process in data
            alert("success")
        },
        failure: function () {
            alert("failure");
        }
    });
}

button.addEventListener("click", () => {
    // TODO: end of quiz logic
    if(availableQuestions.length === 0) {
        submitResults();
        return;
    }
    resetState()
    getNextQuestion()
});

options.forEach(option => {
    option.addEventListener("click", event => {
        if(!allowUserAnswer) return;

        allowUserAnswer = false;

        // track quiz results in order to send back to Django View
        const selectedOption = event.target;
        const selectedAnswer = selectedOption.dataset["num"];
        const isCorrect = parseInt(selectedAnswer) === currentQuestion.correct_answer;
        results[currentQuestion['word_id']] = isCorrect;

        // indicate to user if they were correct
        const resultClass = isCorrect ? 'correct' : 'incorrect';
        selectedOption.parentElement.classList.add(resultClass);

        // if user was incorrect, highlight the correct answer
        if(!isCorrect) {
            options.forEach(option => {
                if(parseInt(option.dataset["num"]) === currentQuestion.correct_answer) {
                    option.parentElement.classList.add('correct');
                }
            })
        }
        button.style.display = "block";
        button.innerText = availableQuestions.length > 0 ? "Continue" : "Submit Your Results";
    });
});

startQuiz();