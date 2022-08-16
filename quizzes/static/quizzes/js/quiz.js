// DOM elements manipulated by the quiz
const quizLandingBlock = document.getElementById("quiz-landing");
const quizBlock = document.getElementById("quiz");
const quizStartButton = document.getElementById("quiz-start-button");
const progressBar = document.getElementById("quiz-progress");
const scoreBar = document.getElementById("score");
const question = document.getElementById("question-header");
const options = Array.from(document.getElementsByClassName("option-text"));
const continueButton = document.getElementById("continue")
const resultsForm = document.getElementById("results-form")
const resultsData = document.getElementById("results-data")

// extract quiz data from JSON received passed by the view
const quizData = JSON.parse(document.getElementById('quiz-data').textContent);
let questions = quizData['questions'];
const CORRECT_ANSWER_PTS = quizData['correct_pts'];
const originIcon = quizData['origin_icon'];
const targetIcon = quizData['target_icon'];

// class names for styling unanswered/correct/incorrect questions
const initialClass = "is-outlined";
const correctClass = "is-success";
const incorrectClass = "is-danger";

// variables used by the quiz loop
const totalQuestions = questions.length;
let currentQuestion = {};
let score = 0;
let questionCounter = 0;
let results = {};
let availableQuestions = [];
let allowUserAnswer = false;

// CSRF token, required when posting back the results
const csrftoken = getCookie('csrftoken');
// const alsotoken = $("input[name=csrfmiddlewaretoken]").val() jQuery version if also using CSRF in template

// getCookie() taken from Django docs, see https://docs.djangoproject.com/en/4.0/ref/csrf/
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

startQuiz = () => {
    availableQuestions = [... questions];
    progressBar.setAttribute("max", totalQuestions)
    getNextQuestion();
};

getNextQuestion = () => {
    if(availableQuestions.length === 0) {
        console.log("Shouldn't be able to get here! Quiz tried to run with no questions");
        return;
    }
    continueButton.style.display = "none";

    // question order is shuffled on the client side
    let questionIndex = Math.floor(Math.random() * availableQuestions.length);
    currentQuestion = availableQuestions[questionIndex];

    // update the question in the DOM
    question.firstElementChild.innerText = getDirectionStr(currentQuestion["origin_to_target"]);
    question.lastElementChild.innerText = currentQuestion["word"];

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
        option.classList.remove(correctClass, incorrectClass);
    })
}

// INACTIVE
submitResults = () => {
    $.ajax({
        url: '',
        type: "POST",
        headers: {'X-CSRFToken': csrftoken},
        dataType: "json",
        data: {results: JSON.stringify(results)},
        success: function () {
            // any process in data
            //alert("success")
        },
        failure: function () {
            alert("failure");
        }
    });
}

quizStartButton.addEventListener("click", () => {
    quizLandingBlock.style.display = "none";
    quizBlock.style.display = "block";
    startQuiz();
});

continueButton.addEventListener("click", () => {
    // check if the quiz has ended
    if(availableQuestions.length === 0) {
        resultsData.value = JSON.stringify(results)
        resultsForm.submit();
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
        const isCorrect = parseInt(selectedAnswer) === currentQuestion["correct_answer"];
        results[currentQuestion['word_id']] = isCorrect;

        // indicate to user if they were correct
        const resultClass = isCorrect ? correctClass : incorrectClass;
        selectedOption.classList.remove(initialClass);
        selectedOption.classList.add(resultClass);

        // if user was incorrect, highlight the correct answer
        if(!isCorrect) {
            options.forEach(option => {
                if(parseInt(option.dataset["num"]) === currentQuestion["correct_answer"]) {
                    option.classList.remove(initialClass);
                    option.classList.add(correctClass);
                }
            })
        }
        else {
            updateScore(CORRECT_ANSWER_PTS);
        }

        // update progress bar
        progressBar.innerText = (questionCounter++).toString();
        progressBar.setAttribute("value", (questionCounter).toString())

        continueButton.style.display = "block";
        continueButton.innerText = availableQuestions.length > 0 ? "Continue..." : "Submit Your Results";
    });
});

updateScore = num => {
    score += num;
    scoreBar.innerText = `${score} pts`;
}

getDirectionStr = is_forwards => {
    return is_forwards ? `${originIcon} → ${targetIcon}`: `${targetIcon} → ${originIcon}`;
}