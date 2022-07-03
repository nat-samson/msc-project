const question = document.getElementById("question");
const options = Array.from(document.getElementsByClassName("option-detail"));
//console.log(options)

let currentQuestion = {};
let score = 0;
let questionCounter = 0;
let results = {};
let availableQuestions = []

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

// TODO: replace with data from settings
const CORRECT_ANSWER_PTS = 10;
const INCORRECT_ANSWER_PTS = -2;

startQuiz = () => {
    availableQuestions = [... questions];
    //console.log(availableQuestions);
    getNextQuestion();
};

getNextQuestion = () => {
    questionCounter++;

    // question order is shuffled on the client side
    let questionIndex = Math.floor(Math.random() * availableQuestions.length);
    //currentQuestion = availableQuestions.splice(questionIndex, 1);
    currentQuestion = availableQuestions[questionIndex];

    // update the question in the DOM
    question.innerText = currentQuestion.word;

    options.forEach(option => {
        const optionNum = option.dataset['num'];
        option.innerText = currentQuestion['options'][optionNum];
    }
    )
    console.log(currentQuestion)

    // track quiz results in order to send back to Django View (update later to include actual user answer)
    results[currentQuestion['word_id']] = false;

};

startQuiz();