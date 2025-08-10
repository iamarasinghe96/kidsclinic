// Global variables
let currentPatientRegNumber = null;
let lastSelectedPatient = null;
let searchTimeout = null;

// Initialize page when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize search functionality
    const searchInput = document.getElementById('search_query');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(searchPatients, 300);
        });
    }

    // Initialize patient item click handlers
    initializePatientHandlers();
    
    // Set max date for date inputs to today
    const dateInputs = document.querySelectorAll('input[type="date"]');
    const today = new Date().toISOString().split('T')[0];
    dateInputs.forEach(input => {
        if (!input.value) {
            input.max = today;
        }
    });

    // Initialize form toggle
    const newPatientBtn = document.getElementById('new-patient-btn');
    const returningPatientBtn = document.getElementById('returning-patient-btn');

    if (newPatientBtn && returningPatientBtn) {
        newPatientBtn.addEventListener('click', () => showForm('new'));
        returningPatientBtn.addEventListener('click', () => showForm('returning'));
    }
});

// Consultant selection
function selectConsultant() {
    const select = document.getElementById('consultantSelect');
    if (select.value) {
        window.location.href = `/consultant?consultant_id=${select.value}`;
    }
}

// Initialize patient click handlers
function initializePatientHandlers() {
    document.querySelectorAll('.patient-item').forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const regNumber = this.dataset.regNumber;
            loadPatientInfo(regNumber);
            
            // Update active state
            document.querySelectorAll('.patient-item').forEach(i => i.classList.remove('active'));
            this.classList.add('active');
            
            // Store as last selected
            lastSelectedPatient = regNumber;
        });
    });
}

// Search patients
function searchPatients() {
    const query = document.getElementById('search_query').value.trim();
    const resultsDiv = document.getElementById('searchResults');
    const resultsList = document.getElementById('searchResultsList');
    
    if (query.length < 2) {
        resultsDiv.style.display = 'none';
        return;
    }
    
    fetch(`/search_patients?query=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            resultsList.innerHTML = '';
            
            if (data.length > 0) {
                data.forEach(patient => {
                    const item = document.createElement('div');
                    item.className = 'list-group-item list-group-item-action';
                    item.innerHTML = `
                        <div class="d-flex w-100 justify-content-between">
                            <h6 class="mb-1">${patient.full_name}</h6>
                            <small>${patient.registration_number}</small>
                        </div>
                        <p class="mb-1">Contact: ${patient.contact_number}</p>
                        <small>Consultant: ${patient.consultant}</small>
                    `;
                    item.addEventListener('click', () => {
                        document.getElementById('returning_reg_number').value = patient.registration_number;
                        resultsDiv.style.display = 'none';
                        document.getElementById('search_query').value = '';
                    });
                    resultsList.appendChild(item);
                });
                resultsDiv.style.display = 'block';
            } else {
                resultsList.innerHTML = '<div class="list-group-item text-muted">No patients found</div>';
                resultsDiv.style.display = 'block';
            }
        })
        .catch(error => {
            console.error('Search error:', error);
        });
}

// Load patient details for returning patient
function loadPatientDetails() {
    const regNumber = document.getElementById('returning_reg_number').value.trim();
    
    if (!regNumber) {
        alert('Please enter a registration number');
        return;
    }
    
    fetch(`/get_patient/${regNumber}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Patient not found');
            }
            return response.json();
        })
        .then(data => {
            // Show patient details in modal or update form
            showPatientDetailsModal(data);
        })
        .catch(error => {
            alert('Patient not found with this registration number');
        });
}

// Show patient details modal
function showPatientDetailsModal(patient) {
    const modalContent = document.getElementById('patientDetailsContent');
    modalContent.innerHTML = `
        <div class="row">
            <div class="col-md-6">
                <p><strong>Name:</strong> ${patient.full_name}</p>
                <p><strong>Date of Birth:</strong> ${patient.date_of_birth}</p>
                <p><strong>Gender:</strong> ${patient.gender}</p>
            </div>
            <div class="col-md-6">
                <p><strong>Contact:</strong> ${patient.contact_number}</p>
                <p><strong>Address:</strong> ${patient.address}</p>
            </div>
        </div>
    `;
    
    const modal = new bootstrap.Modal(document.getElementById('patientDetailsModal'));
    modal.show();
}

// Load patient information for consultant page
function loadPatientInfo(regNumber) {
    fetch(`/get_patient_details/${regNumber}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            
            displayPatientInfo(data);
            currentPatientRegNumber = regNumber;
            
            // Show patient actions buttons
            document.getElementById('patientActions').style.display = 'block';
        })
        .catch(error => {
            console.error('Error loading patient info:', error);
            const patientInfo = document.getElementById('patientInfo');
            patientInfo.innerHTML = `
                <div class="alert alert-danger">
                    <i data-feather="alert-circle"></i>
                    Error loading patient information
                </div>
            `;
            feather.replace();
        });
}

// Display patient information
function displayPatientInfo(patient) {
    const patientInfo = document.getElementById('patientInfo');
    patientInfo.innerHTML = `
        <div class="patient-details">
            <div class="info-row">
                <span class="info-label">Registration #:</span>
                <span class="info-value">${patient.registration_number}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Name:</span>
                <span class="info-value">${patient.full_name}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Age:</span>
                <span class="info-value">${patient.age} years</span>
            </div>
            <div class="info-row">
                <span class="info-label">Gender:</span>
                <span class="info-value">${patient.gender}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Date of Birth:</span>
                <span class="info-value">${patient.date_of_birth}</span>
            </div>
            
            <div class="mt-3">
                <h6>Recent Visits:</h6>
                ${patient.recent_visits.length > 0 ? 
                    patient.recent_visits.map(date => `<small class="d-block">${date}</small>`).join('') :
                    '<small class="text-muted">No previous visits</small>'
                }
            </div>

        </div>
    `;
    feather.replace();
}

// Complete consultation
function completeConsultation() {
    if (!currentPatientRegNumber) {
        alert('No patient selected');
        return;
    }
    
    if (confirm('Mark this consultation as completed?')) {
        document.getElementById('completeRegNumber').value = currentPatientRegNumber;
        document.getElementById('completeForm').submit();
    }
}

// Reset patient information
function resetPatientInfo() {
    const patientInfo = document.getElementById('patientInfo');
    patientInfo.innerHTML = `
        <div class="text-center text-muted">
            <i data-feather="info"></i>
            <p>Select a patient from the queue to view details</p>
        </div>
    `;
    
    // Clear active states
    document.querySelectorAll('.patient-item').forEach(item => {
        item.classList.remove('active');
    });
    
    // If there was a last selected patient, load them
    if (lastSelectedPatient) {
        loadPatientInfo(lastSelectedPatient);
        // Find and activate the last selected patient item
        document.querySelectorAll('.patient-item').forEach(item => {
            if (item.dataset.regNumber === lastSelectedPatient) {
                item.classList.add('active');
            }
        });
    }
    
    currentPatientRegNumber = null;
    document.getElementById('patientActions').style.display = 'none';
    feather.replace();
}

// Print patient information
function printPatientInfo() {
    if (!currentPatientRegNumber) {
        alert('No patient selected');
        return;
    }
    
    fetch(`/get_patient_details/${currentPatientRegNumber}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            
            // Create a new window for printing
            const printWindow = window.open('', '_blank');
            const currentDateTime = new Date().toLocaleString();
            
            const printContent = `
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Patient Consultation - ${data.full_name}</title>
                    <style>
                        * {
                            margin: 0;
                            padding: 0;
                            box-sizing: border-box;
                        }
                        
                        body {
                            font-family: Arial, sans-serif;
                            font-size: 12px;
                            line-height: 1.4;
                            background: white;
                            color: black;
                            padding: 20px;
                        }
                        
                        .patient-info {
                            position: absolute;
                            top: 20px;
                            right: 20px;
                            border: 2px solid #000;
                            padding: 10px;
                            width: 200px;
                            background: white;
                        }
                        
                        .patient-info p {
                            margin: 8px 0;
                        }
                        
                        .patient-info strong {
                            font-weight: bold;
                        }
                        
                        .consultation-notes {
                            margin-top: 180px;
                            margin-left: 20px;
                            margin-right: 20px;
                        }
                        
                        .consultation-notes h3 {
                            font-size: 16px;
                            margin-bottom: 25px;
                            border-bottom: 2px solid #000;
                            padding-bottom: 8px;
                            font-weight: bold;
                        }
                        
                        .line {
                            border-bottom: 1px solid #000;
                            height: 25px;
                            margin-bottom: 25px;
                            width: 100%;
                        }
                        
                        @media print {
                            body { margin: 0; padding: 20px; }
                        }
                    </style>
                </head>
                <body>
                    <div class="patient-info">
                        <p><strong>Registration #:</strong> ${data.registration_number}</p>
                        <p><strong>Name:</strong> ${data.full_name}</p>
                        <p><strong>Age:</strong> ${data.age} years</p>
                        <p><strong>Gender:</strong> ${data.gender}</p>
                        <p><strong>Date of Birth:</strong> ${data.date_of_birth}</p>
                        <p><strong>Visit Date/Time:</strong> ${currentDateTime}</p>
                    </div>
                </body>
                </html>
            `;
            
            printWindow.document.open();
            printWindow.document.write(printContent);
            printWindow.document.close();
            
            // Wait for content to load, then print and close
            printWindow.onload = function() {
                setTimeout(() => {
                    printWindow.print();
                    printWindow.close();
                }, 500);
            };
        })
        .catch(error => {
            alert('Error loading patient information for printing');
        });
}

// Form validation helpers
function validateForm(formId) {
    const form = document.getElementById(formId);
    const requiredFields = form.querySelectorAll('[required]');
    
    for (let field of requiredFields) {
        if (!field.value.trim()) {
            field.focus();
            alert(`Please fill in the ${field.labels[0].textContent} field`);
            return false;
        }
    }
    
    return true;
}

// Auto-refresh functionality for consultant page
let autoRefreshInterval;

function startAutoRefresh() {
    // Refresh every 10 seconds if on consultant page
    if (window.location.pathname === '/consultant') {
        autoRefreshInterval = setInterval(() => {
            const consultantId = document.getElementById('consultantSelect').value;
            if (consultantId) {
                // Only refresh if no modal is open and no patient is actively selected
                if (!document.querySelector('.modal.show') && !currentPatientRegNumber) {
                    location.reload();
                }
            }
        }, 10000);
    }
}

function stopAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
    }
}

// Start auto-refresh when page loads
document.addEventListener('DOMContentLoaded', startAutoRefresh);

// Stop auto-refresh when page unloads
window.addEventListener('beforeunload', stopAutoRefresh);


// --- New functions from snippet ---

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