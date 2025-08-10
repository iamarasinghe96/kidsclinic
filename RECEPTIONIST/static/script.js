
// Global variables
let currentPatientRegNumber = null;
let searchTimeout = null;

document.addEventListener('DOMContentLoaded', function() {
    // Initialize search functionality
    const patientSearch = document.getElementById('patient-search');
    if (patientSearch) {
        patientSearch.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                searchPatients(this.value);
            }, 300);
        });
    }

    // Initialize form toggle
    const newPatientBtn = document.getElementById('new-patient-btn');
    const returningPatientBtn = document.getElementById('returning-patient-btn');
    
    if (newPatientBtn && returningPatientBtn) {
        newPatientBtn.addEventListener('click', () => showForm('new'));
        returningPatientBtn.addEventListener('click', () => showForm('returning'));
    }
});

function showForm(type) {
    const newForm = document.getElementById('new-patient-form');
    const returningForm = document.getElementById('returning-patient-form');
    const newBtn = document.getElementById('new-patient-btn');
    const returningBtn = document.getElementById('returning-patient-btn');

    if (type === 'new') {
        newForm.style.display = 'block';
        returningForm.style.display = 'none';
        newBtn.classList.add('active');
        returningBtn.classList.remove('active');
    } else {
        newForm.style.display = 'none';
        returningForm.style.display = 'block';
        newBtn.classList.remove('active');
        returningBtn.classList.add('active');
    }
}

function searchPatients(query) {
    const resultsContainer = document.getElementById('search-results');
    
    if (!query || query.length < 2) {
        resultsContainer.innerHTML = '';
        return;
    }

    fetch(`/search_patients?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(patients => {
            if (patients.length === 0) {
                resultsContainer.innerHTML = '<div class="search-result-item">No patients found</div>';
                return;
            }

            resultsContainer.innerHTML = patients.map(patient => `
                <div class="search-result-item" onclick="selectPatient(${patient.id})">
                    <strong>${patient.full_name}</strong><br>
                    <small>Reg: ${patient.registration_number} | DOB: ${patient.date_of_birth} | Consultant: ${patient.consultant_name}</small>
                </div>
            `).join('');
        })
        .catch(error => {
            console.error('Search error:', error);
            resultsContainer.innerHTML = '<div class="search-result-item">Search error occurred</div>';
        });
}

function selectPatient(patientId) {
    fetch(`/get_patient_details_by_id/${patientId}`)
        .then(response => response.json())
        .then(patient => {
            // Populate the returning patient form
            document.getElementById('selected-patient-name').textContent = patient.full_name;
            document.getElementById('selected-patient-reg').textContent = patient.registration_number;
            document.getElementById('selected-patient-dob').textContent = patient.date_of_birth;
            document.getElementById('selected-patient-contact').textContent = patient.contact_number;
            document.getElementById('selected-patient-consultant').textContent = patient.consultant_name;
            
            // Set hidden field
            document.getElementById('selected-patient-id').value = patient.id;
            
            // Show patient details and hide search results
            document.getElementById('patient-details').style.display = 'block';
            document.getElementById('search-results').innerHTML = '';
            document.getElementById('patient-search').value = '';
        })
        .catch(error => {
            console.error('Error fetching patient details:', error);
            alert('Error loading patient details');
        });
}

function clearSelection() {
    document.getElementById('patient-details').style.display = 'none';
    document.getElementById('selected-patient-id').value = '';
    document.getElementById('patient-search').value = '';
}
