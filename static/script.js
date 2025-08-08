// Global variables
let currentPatientRegNumber = null;
let lastSelectedPatient = null;

// Initialize page when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize search functionality
    const searchInput = document.getElementById('search_query');
    if (searchInput) {
        let searchTimeout;
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
            
            // Enable print and complete consultation buttons
            document.getElementById('printBtn').disabled = false;
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
            
            <div class="mt-3">
                <button class="btn btn-success btn-sm" onclick="completeConsultation()">
                    <i data-feather="check"></i>
                    Complete Consultation
                </button>
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
    document.getElementById('printBtn').disabled = true;
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
            
            const printInfo = document.getElementById('printPatientInfo');
            const currentDateTime = new Date().toLocaleString();
            
            printInfo.innerHTML = `
                <p><strong>Registration #:</strong><br>${data.registration_number}</p>
                <p><strong>Name:</strong><br>${data.full_name}</p>
                <p><strong>Age:</strong><br>${data.age} years</p>
                <p><strong>Gender:</strong><br>${data.gender}</p>
                <p><strong>Date of Birth:</strong><br>${data.date_of_birth}</p>
                <p><strong>Visit Date/Time:</strong><br>${currentDateTime}</p>
            `;
            
            // Show the print template and trigger print
            const printTemplate = document.getElementById('printTemplate');
            printTemplate.style.display = 'block';
            
            // Trigger print after a short delay to ensure content is rendered
            setTimeout(() => {
                window.print();
                // Hide the print template after printing
                printTemplate.style.display = 'none';
            }, 100);
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
    // Refresh every 30 seconds if on consultant page
    if (window.location.pathname === '/consultant') {
        autoRefreshInterval = setInterval(() => {
            const consultantId = document.getElementById('consultantSelect').value;
            if (consultantId) {
                // Only refresh if no modal is open
                if (!document.querySelector('.modal.show')) {
                    location.reload();
                }
            }
        }, 30000);
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
