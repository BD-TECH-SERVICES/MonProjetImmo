// Variables globales
let currentQuestionIndex = 0;
let answers = {};

// Définition des questions pour l'achat
const questions = [
    {
        id: 'type_bien',
        question: 'Quel type de bien recherchez-vous ?',
        type: 'select',
        options: [
            {value: 'maison', label: 'Maison'},
            {value: 'appartement', label: 'Appartement'},
            {value: 'terrain', label: 'Terrain'},
            {value: 'local_commercial', label: 'Local commercial'},
            {value: 'autre', label: 'Autre'}
        ],
        required: true,
        icon: 'fa-home'
    },
    {
        id: 'budget',
        question: 'Quel est votre budget maximum ?',
        type: 'number',
        placeholder: 'Ex: 250000',
        suffix: '€',
        required: true,
        icon: 'fa-euro-sign',
        min: 0,
        step: 1000
    }
];

// Fonction pour afficher une question
function afficherQuestion(index) {
    if (index < 0 || index >= questions.length) return false;
    
    const question = questions[index];
    const questionText = document.getElementById('question-text');
    const optionsContainer = document.getElementById('options-container');
    
    // Mettre à jour le texte de la question
    questionText.innerHTML = `<i class="fas ${question.icon} me-2"></i>${question.question}`;
    
    // Vider le conteneur d'options
    optionsContainer.innerHTML = '';
    
    // Afficher les options en fonction du type de question
    switch (question.type) {
        case 'select':
        case 'radio':
            question.options.forEach(option => {
                const div = document.createElement('div');
                div.className = 'form-check mb-2';
                div.innerHTML = `
                    <input class="form-check-input" type="radio" 
                           name="${question.id}" 
                           id="${question.id}_${option.value}" 
                           value="${option.value}"
                           ${answers[question.id] === option.value ? 'checked' : ''}>
                    <label class="form-check-label" for="${question.id}_${option.value}">
                        ${option.label}
                    </label>
                `;
                optionsContainer.appendChild(div);
            });
            break;
            
        case 'number':
            const inputGroup = document.createElement('div');
            inputGroup.className = 'input-group';
            inputGroup.innerHTML = `
                <input type="number" class="form-control form-control-lg" 
                       id="${question.id}" 
                       value="${answers[question.id] || ''}" 
                       placeholder="${question.placeholder || ''}"
                       ${question.min ? `min="${question.min}"` : ''}
                       ${question.step ? `step="${question.step}"` : ''}>
                <span class="input-group-text">${question.suffix || ''}</span>
            `;
            optionsContainer.appendChild(inputGroup);
            break;
    }
    
    // Mettre à jour l'affichage de la progression
    document.getElementById('current-question').textContent = index + 1;
    const progress = ((index + 1) / questions.length) * 100;
    document.getElementById('progress-bar').style.width = `${progress}%`;
    
    // Mettre à jour les boutons de navigation
    updateNavigationButtons();
    
    return true;
}

// Fonction pour sauvegarder la réponse actuelle
function saveAnswer() {
    if (currentQuestionIndex >= questions.length) return true;
    
    const question = questions[currentQuestionIndex];
    let value = '';
    let isValid = true;
    
    // Récupérer la valeur en fonction du type de question
    switch (question.type) {
        case 'select':
        case 'radio':
            const selectedRadio = document.querySelector(`input[name="${question.id}"]:checked`);
            value = selectedRadio ? selectedRadio.value : '';
            isValid = !question.required || (value !== '');
            break;
            
        case 'number':
            const input = document.getElementById(question.id);
            value = input ? input.value : '';
            isValid = !question.required || (value !== '' && !isNaN(value));
            if (isValid && value !== '') value = parseFloat(value);
            break;
    }
    
    // Valider la réponse
    if (question.required && !isValid) {
        alert('Veuillez répondre à cette question avant de continuer.');
        return false;
    }
    
    // Sauvegarder la réponse
    answers[question.id] = value;
    return true;
}

// Fonction pour passer à la question suivante
function questionSuivante() {
    if (saveAnswer()) {
        currentQuestionIndex++;
        if (currentQuestionIndex < questions.length) {
            afficherQuestion(currentQuestionIndex);
        } else {
            // Afficher le récapitulatif si c'est la dernière question
            afficherRecapitulatif();
        }
    }
}

// Fonction pour revenir à la question précédente
function questionPrecedente() {
    if (currentQuestionIndex > 0) {
        currentQuestionIndex--;
        afficherQuestion(currentQuestionIndex);
    }
}

// Fonction pour mettre à jour les boutons de navigation
function updateNavigationButtons() {
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    const submitBtn = document.getElementById('submit-btn');
    
    // Mettre à jour le bouton Précédent
    prevBtn.style.display = currentQuestionIndex === 0 ? 'none' : 'block';
    
    // Mettre à jour les boutons Suivant/Terminer
    const isLastQuestion = currentQuestionIndex === questions.length - 1;
    nextBtn.style.display = isLastQuestion ? 'none' : 'block';
    submitBtn.style.display = isLastQuestion ? 'block' : 'none';
}

// Fonction pour afficher le récapitulatif
function afficherRecapitulatif() {
    const container = document.getElementById('question-container');
    let html = `
        <div class="recap-container">
            <h3 class="mb-4"><i class="fas fa-clipboard-check me-2"></i>Récapitulatif de votre projet d'achat</h3>
            <div class="recap-answers">
    `;
    
    // Parcourir toutes les questions et afficher les réponses
    questions.forEach(question => {
        if (answers[question.id] !== undefined) {
            let answerText = answers[question.id];
            
            // Formater la réponse en fonction du type de question
            if (question.type === 'select' || question.type === 'radio') {
                const selectedOption = question.options.find(opt => opt.value === answerText);
                answerText = selectedOption ? selectedOption.label : answerText;
            } else if (question.type === 'number' && question.suffix) {
                answerText += ' ' + question.suffix;
            }
            
            html += `
                <div class="recap-item mb-3">
                    <div class="recap-question">
                        <i class="fas ${question.icon} me-2"></i>${question.question}
                    </div>
                    <div class="recap-answer">
                        ${answerText || '<span class="text-muted">Non renseigné</span>'}
                    </div>
                </div>
            `;
        }
    });
    
    html += `
            </div>
        </div>
    `;
    
    container.innerHTML = html;
    
    // Masquer les boutons de navigation
    document.getElementById('prev-btn').style.display = 'none';
    document.getElementById('next-btn').style.display = 'none';
    document.getElementById('submit-btn').style.display = 'block';
}

// Initialisation du questionnaire
document.addEventListener('DOMContentLoaded', function() {
    // Mettre à jour le nombre total de questions
    document.getElementById('total-questions').textContent = questions.length;
    
    // Afficher la première question
    afficherQuestion(0);
    
    // Gestion des boutons
    document.getElementById('prev-btn').addEventListener('click', questionPrecedente);
    document.getElementById('next-btn').addEventListener('click', questionSuivante);
    document.getElementById('submit-btn').addEventListener('click', function(e) {
        e.preventDefault();
        if (saveAnswer()) {
            document.querySelector('form').submit();
        }
    });
});
