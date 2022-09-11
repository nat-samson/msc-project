/**
 * @file Single-page application logic for running the multiple-choice quiz.
 * @author Nathaniel Samson
 */

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

/** Clicking the 'Let's Go!' button hides the landing page and starts the quiz. */
quizStartButton.addEventListener("click", () => {
    quizLandingBlock.style.display = "none";
    quizBlock.style.display = "block";
    startQuiz();
});

/** Clicking the 'Continue...' button moves the quiz onto the next question, or ends the quiz if no more questions. */
continueButton.addEventListener("click", () => {
    if(availableQuestions.length === 0) {
        // if the quiz is over, submit the results
        resultsData.value = JSON.stringify(results);
        resultsForm.submit();
        return;
    }
    resetState();
    getNextQuestion();
});

/** Logic for handling the user answering the current question. */
options.forEach(option => {
    option.addEventListener("click", event => {
        // Only permit user input once per question (user cannot change their answer)
        if(!allowUserAnswer) return;
        allowUserAnswer = false;

        // check if user is correct, record their answer
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

        // update progress bar and get ready for the next question / end of quiz
        updateProgress();
        continueButton.style.display = "block";
        continueButton.innerText = availableQuestions.length > 0 ? "Continue..." : "Submit Your Results";
    });
});

/** Start the Quiz! Set up the questions to come and the initial Quiz UI. */
startQuiz = () => {
    availableQuestions = [... questions];
    progressBar.setAttribute("max", totalQuestions);
    getNextQuestion();
};

/** Refresh the Quiz UI with the next question and update the list of questions to come. */
getNextQuestion = () => {
    if(availableQuestions.length === 0) {
        console.log("ERROR: Shouldn't be able to get here! Quiz tried to run with no questions.");
        return;
    }
    continueButton.style.display = "none";

    // pick a random question from the pile
    let questionIndex = Math.floor(Math.random() * availableQuestions.length);
    currentQuestion = availableQuestions[questionIndex];

    // update the question and associated options displayed in the UI
    question.firstElementChild.innerText = getDirectionStr(currentQuestion["origin_to_target"]);
    question.lastElementChild.innerText = currentQuestion["word"];
    options.forEach(option => {
            const optionNum = option.dataset['num'];
            option.innerText = currentQuestion['options'][optionNum];
        }
    )

    // remove the question from the pile
    availableQuestions.splice(questionIndex, 1);
    allowUserAnswer = true;
};

/** Reset the highlighting of the options when proceeding to the next question. */
resetState = () => {
    options.forEach(option => {
        option.classList.remove(correctClass, incorrectClass);
    })
}

/** Update the current score and display it in the Quiz UI. */
updateScore = num => {
    score += num;
    scoreBar.innerText = `${score} pts`;
}

/** Update the progress bar and display it in the Quiz UI. */
updateProgress = () => {
    progressBar.innerText = (questionCounter++).toString();
    progressBar.setAttribute("value", (questionCounter).toString());
}

/**
 * Get a string that represents the direction of the current question, i.e. "Flag1 -> Flag2".
 * @param {boolean} is_forwards - A boolean indicating the question direction.
 * @returns {string} - A string representing the question direction in a human-readable format.
 */
getDirectionStr = is_forwards => {
    return is_forwards ? `${originIcon} → ${targetIcon}`: `${targetIcon} → ${originIcon}`;
}