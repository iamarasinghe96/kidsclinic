// Global variables for patient management
let currentPatientRegNumber = null;
let lastSelectedPatient = null;
let isReturningPatientMode = false;

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Clinic system initialized');

    // Initialize form submission
    const patientForm = document.getElementById('patientForm');
    if (patientForm) {
        patientForm.addEventListener('submit', handlePatientRegistration);
    }

    // Initialize edit form submission
    const editPatientForm = document.getElementById('editPatientForm');
    if (editPatientForm) {
        editPatientForm.addEventListener('submit', function(e) {
            e.preventDefault();
            savePatientChanges();
        });
    }

    // Initialize Feather icons
    if (typeof feather !== 'undefined') {
        feather.replace();
    }
    
    // Auto-refresh functionality for queue management
    if (window.location.pathname.includes('/receptionist') || 
        window.location.pathname.includes('/consultant')) {
        startAutoRefresh();
    }
    
    // Load initial data
    refreshPatientList();
});

// Auto-refresh functionality
function startAutoRefresh() {
    // Check for updates every 10 seconds
    setInterval(function() {
        if (!document.hidden) { // Only refresh if page is visible
            checkForUpdates();
        }
    }, 10000);
}

function checkForUpdates() {
    // Simple implementation - could be enhanced with AJAX polling
    const lastRefresh = localStorage.getItem('lastRefresh');
    const now = Date.now();

    if (!lastRefresh || (now - parseInt(lastRefresh)) > 30000) {
        localStorage.setItem('lastRefresh', now.toString());
        // Optionally reload page or update specific sections
    }
}

// Utility function to show loading state
function showLoading(element) {
    if (element) {
        element.innerHTML = '<div class="text-center"><i data-feather="loader" class="spinning"></i> Loading...</div>';
        if (typeof feather !== 'undefined') {
            feather.replace();
        }
    }
}

// Utility function to handle errors
function handleError(error, message = 'An error occurred') {
    console.error('Error:', error);
    alert(message);
}

// Print functionality
function printElement(elementId) {
    const element = document.getElementById(elementId);
    if (!element) {
        alert('Print content not found');
        return;
    }

    const printWindow = window.open('', '_blank');
    printWindow.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>Print - The Kids Clinic</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .no-print { display: none; }
                @media print {
                    body { margin: 0; }
                    .no-print { display: none !important; }
                }
            </style>
        </head>
        <body>
            ${element.innerHTML}
        </body>
        </html>
    `);
    printWindow.document.close();
    printWindow.print();
    printWindow.close();
}

// Form validation utilities
function validateForm(formElement) {
    const requiredFields = formElement.querySelectorAll('[required]');
    let isValid = true;

    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
        }
    });

    return isValid;
}

// Date formatting utility
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-LK', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Registration number validation
function isValidRegistrationNumber(regNumber) {
    // Format: DDMMYYXXX (e.g., 100124001)
    const regex = /^\d{9}$/;
    return regex.test(regNumber);
}

// Age calculation from date of birth
function calculateAge(dateOfBirth) {
    const today = new Date();
    const birthDate = new Date(dateOfBirth);
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();

    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
        age--;
    }

    return age;
}

// Handle patient registration form submission
function handlePatientRegistration(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const patientData = Object.fromEntries(formData.entries());
    
    // Validate required fields
    if (!patientData.name || !patientData.consultant_id) {
        showAlert('Please fill in all required fields', 'danger');
        return;
    }
    
    fetch('/api/register_patient', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(patientData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSuccessModal(`Patient registered successfully!<br>
                Registration Number: <strong>${data.registration_number}</strong>`);
            clearForm();
            refreshPatientList();
        } else {
            showAlert(data.error || 'Registration failed', 'danger');
        }
    })
    .catch(error => {
        console.error('Registration error:', error);
        showAlert('Registration failed. Please try again.', 'danger');
    });
}

// Clear the registration form
function clearForm() {
    const form = document.getElementById('patientForm');
    if (form) {
        form.reset();
    }
    
    // Hide returning patient section
    const returningSection = document.getElementById('returningPatientSection');
    if (returningSection) {
        returningSection.style.display = 'none';
        isReturningPatientMode = false;
    }
    
    // Clear search results
    const searchResults = document.getElementById('searchResults');
    if (searchResults) {
        searchResults.innerHTML = '';
    }
}

// Toggle returning patient search
function toggleReturningPatient() {
    const returningSection = document.getElementById('returningPatientSection');
    isReturningPatientMode = !isReturningPatientMode;
    
    if (isReturningPatientMode) {
        returningSection.style.display = 'block';
        document.getElementById('patient_search').focus();
    } else {
        returningSection.style.display = 'none';
        clearSearch();
    }
}

// Search for existing patients
function searchPatients() {
    const searchTerm = document.getElementById('patient_search').value.trim();
    const searchResults = document.getElementById('searchResults');
    
    if (searchTerm.length < 2) {
        searchResults.innerHTML = '';
        return;
    }
    
    fetch(`/api/search_patients?q=${encodeURIComponent(searchTerm)}`)
        .then(response => response.json())
        .then(patients => {
            if (patients.length === 0) {
                searchResults.innerHTML = '<p class="text-muted small">No patients found</p>';
                return;
            }
            
            searchResults.innerHTML = patients.map(patient => `
                <div class="search-result-item" onclick="selectReturningPatient('${patient.registration_number}')">
                    <strong>${patient.name}</strong> - ${patient.registration_number}
                    <br><small class="text-muted">${patient.consultant_name} | Age: ${patient.age || 'N/A'}</small>
                </div>
            `).join('');
        })
        .catch(error => {
            console.error('Search error:', error);
            searchResults.innerHTML = '<p class="text-danger small">Search failed</p>';
        });
}

// Select a returning patient
function selectReturningPatient(regNumber) {
    fetch(`/api/patient_details/${regNumber}`)
        .then(response => response.json())
        .then(patient => {
            if (patient.error) {
                showAlert(patient.error, 'danger');
                return;
            }
            
            // Fill the form with patient data
            document.getElementById('patient_name').value = patient.name;
            document.getElementById('patient_age').value = patient.age || '';
            document.getElementById('parent_name').value = patient.parent_name || '';
            document.getElementById('patient_phone').value = patient.phone || '';
            document.getElementById('patient_email').value = patient.email || '';
            document.getElementById('consultant').value = patient.consultant_id || '';
            
            // Hide returning patient section
            toggleReturningPatient();
            
            showAlert(`Patient ${patient.name} loaded. Update weight and register for today's visit.`, 'info');
        })
        .catch(error => {
            console.error('Error loading patient:', error);
            showAlert('Error loading patient data', 'danger');
        });
}

// Clear search
function clearSearch() {
    document.getElementById('patient_search').value = '';
    document.getElementById('searchResults').innerHTML = '';
}

// Filter patients by consultant
function filterByConsultant() {
    refreshPatientList();
}

// Load patient information for display
function loadPatientInfo(regNumber) {
    currentPatientRegNumber = regNumber;
    lastSelectedPatient = regNumber;
    
    fetch(`/api/patient_details/${regNumber}`)
        .then(response => response.json())
        .then(patient => {
            if (patient.error) {
                showAlert(patient.error, 'danger');
                return;
            }
            
            displayPatientInfo(patient);
        })
        .catch(error => {
            console.error('Error loading patient info:', error);
            document.getElementById('patientInfo').innerHTML = 
                '<p class="text-danger">Error loading patient information</p>';
        });
}

// Display patient information in the right panel
function displayPatientInfo(patient) {
    const patientInfo = document.getElementById('patientInfo');
    const currentVisit = patient.current_visit;
    
    // Correctly use 'created_at' for visit date as per the intention
    const visitDateTime = currentVisit.created_at ? new Date(currentVisit.created_at).toLocaleString('en-LK', {
        year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
    }) : 'N/A';

    const statusBadge = currentVisit.status === 'waiting' ? 
        '<span class="badge bg-warning text-dark">Waiting</span>' :
        currentVisit.status === 'completed' ?
        '<span class="badge bg-success">Completed</span>' :
        '<span class="badge bg-secondary">No Visit</span>';
    
    patientInfo.innerHTML = `
        <div class="patient-details">
            <div class="d-flex justify-content-between align-items-start mb-3">
                <h6 class="mb-0">${patient.name}</h6>
                ${statusBadge}
            </div>
            
            <div class="patient-info-grid">
                <div class="info-item">
                    <small class="text-muted">Registration #</small>
                    <div>${patient.registration_number}</div>
                </div>
                
                <div class="info-item">
                    <small class="text-muted">Age</small>
                    <div>${patient.age || 'Not specified'}</div>
                </div>
                
                <div class="info-item">
                    <small class="text-muted">Parent/Guardian</small>
                    <div>${patient.parent_name || 'Not specified'}</div>
                </div>
                
                <div class="info-item">
                    <small class="text-muted">Phone</small>
                    <div>${patient.phone || 'Not specified'}</div>
                </div>
                
                <div class="info-item">
                    <small class="text-muted">Email</small>
                    <div>${patient.email || 'Not specified'}</div>
                </div>
                
                <div class="info-item">
                    <small class="text-muted">Consultant</small>
                    <div>${patient.consultant_name}</div>
                </div>
                
                ${currentVisit.weight ? `
                <div class="info-item">
                    <small class="text-muted">Weight</small>
                    <div>${currentVisit.weight} kg</div>
                </div>
                ` : ''}
                
                <div class="info-item">
                    <small class="text-muted">Visit Time</small>
                    <div>${visitDateTime}</div>
                </div>
            </div>
            
            <div class="patient-actions mt-3">
                <button class="btn btn-sm btn-outline-primary me-2" onclick="editPatient('${patient.registration_number}')">
                    <i data-feather="edit" style="width: 14px; height: 14px;"></i>
                    Edit
                </button>
                
                ${currentVisit.status === 'waiting' ? `
                <button class="btn btn-sm btn-outline-success me-2" onclick="completeConsultation(${currentVisit.id})">
                    <i data-feather="check" style="width: 14px; height: 14px;"></i>
                    Complete
                </button>
                ` : ''}
                
                <button class="btn btn-sm btn-outline-info" onclick="printPatient('${patient.registration_number}')">
                    <i data-feather="printer" style="width: 14px; height: 14px;"></i>
                    Print
                </button>
            </div>
        </div>
    `;
    
    feather.replace();
}

// Edit patient information
function editPatient(regNumber) {
    fetch(`/api/patient_details/${regNumber}`)
        .then(response => response.json())
        .then(patient => {
            if (patient.error) {
                showAlert(patient.error, 'danger');
                return;
            }
            
            // Fill edit modal with patient data
            document.getElementById('edit_patient_id').value = patient.id;
            document.getElementById('edit_patient_name').value = patient.name;
            document.getElementById('edit_patient_age').value = patient.age || '';
            document.getElementById('edit_parent_name').value = patient.parent_name || '';
            document.getElementById('edit_patient_phone').value = patient.phone || '';
            document.getElementById('edit_patient_email').value = patient.email || '';
            document.getElementById('edit_consultant').value = patient.consultant_id;
            document.getElementById('edit_patient_weight').value = patient.current_visit.weight || '';
            
            // Show modal
            new bootstrap.Modal(document.getElementById('editPatientModal')).show();
        })
        .catch(error => {
            console.error('Error loading patient for edit:', error);
            showAlert('Error loading patient data', 'danger');
        });
}

// Save patient changes
function savePatientChanges() {
    const patientId = document.getElementById('edit_patient_id').value;
    const updatedData = {
        patient_id: patientId,
        name: document.getElementById('edit_patient_name').value,
        age: document.getElementById('edit_patient_age').value || null,
        parent_name: document.getElementById('edit_parent_name').value,
        phone: document.getElementById('edit_patient_phone').value,
        email: document.getElementById('edit_patient_email').value,
        consultant_id: document.getElementById('edit_consultant').value,
        weight: document.getElementById('edit_patient_weight').value || null
    };
    
    fetch('/api/update_patient', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(updatedData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('Patient information updated successfully', 'success');
            bootstrap.Modal.getInstance(document.getElementById('editPatientModal')).hide();
            refreshPatientList();
            if (currentPatientRegNumber) {
                loadPatientInfo(currentPatientRegNumber);
            }
        } else {
            showAlert(data.error || 'Update failed', 'danger');
        }
    })
    .catch(error => {
        console.error('Update error:', error);
        showAlert('Update failed. Please try again.', 'danger');
    });
}

// Complete consultation
function completeConsultation(visitId) {
    if (!confirm('Mark this consultation as completed?')) {
        return;
    }
    
    fetch('/api/complete_consultation', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ visit_id: visitId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('Consultation completed successfully', 'success');
            refreshPatientList();
            if (currentPatientRegNumber) {
                loadPatientInfo(currentPatientRegNumber);
            }
        } else {
            showAlert(data.error || 'Failed to complete consultation', 'danger');
        }
    })
    .catch(error => {
        console.error('Error completing consultation:', error);
        showAlert('Error completing consultation', 'danger');
    });
}

// Print patient information
function printPatient(regNumber) {
    window.open(`/print_patient/${regNumber}`, '_blank');
}

// Show success modal
function showSuccessModal(message) {
    document.getElementById('successMessage').innerHTML = message;
    new bootstrap.Modal(document.getElementById('successModal')).show();
}

// Show alert message
function showAlert(message, type = 'info') {
    // Remove existing alerts
    const existingAlerts = document.querySelectorAll('.alert');
    existingAlerts.forEach(alert => alert.remove());
    
    // Create new alert
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Insert at top of main content
    const container = document.querySelector('.container-fluid');
    if (container) {
        container.insertBefore(alert, container.firstChild);
    } else {
        // Fallback if container is not found
        document.body.insertBefore(alert, document.body.firstChild);
    }
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (alert.parentNode) {
            alert.remove();
        }
    }, 5000);
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
        });
    });
}

// Load and refresh patient list
function refreshPatientList() {
    const consultantId = document.getElementById('consultantFilter')?.value || '';
    const url = consultantId ? `/api/patients?consultant_id=${consultantId}` : '/api/patients';
    
    fetch(url)
        .then(response => response.json())
        .then(patients => {
            const patientsList = document.getElementById('patientsList');
            
            if (patients.length === 0) {
                patientsList.innerHTML = '<p class="text-muted text-center">No patients registered today</p>';
                return;
            }
            
            patientsList.innerHTML = patients.map(patient => {
                const statusColor = patient.current_visit.status === 'waiting' ? 'warning' : 
                                   patient.current_visit.status === 'completed' ? 'success' : 'secondary';
                const statusText = patient.current_visit.status === 'waiting' ? 'Waiting' : 
                                  patient.current_visit.status === 'completed' ? 'Completed' : 'No Visit';
                                  
                return `
                    <div class="patient-item" data-reg-number="${patient.registration_number}">
                        <div class="d-flex justify-content-between align-items-start">
                            <div class="flex-grow-1">
                                <h6 class="mb-1">${patient.name} 
                                    <span class="badge bg-${statusColor} ms-2">${statusText}</span>
                                </h6>
                                <small class="text-muted">
                                    <i data-feather="hash" style="width: 12px; height: 12px;"></i>
                                    ${patient.registration_number}
                                    <span class="ms-2">
                                        <i data-feather="user-check" style="width: 12px; height: 12px;"></i>
                                        ${patient.consultant_name}
                                    </span>
                                    ${patient.age ? `<span class="ms-2"><i data-feather="calendar" style="width: 12px; height: 12px;"></i> ${patient.age}y</span>` : ''}
                                    ${patient.current_visit.weight ? `<span class="ms-2"><i data-feather="activity" style="width: 12px; height: 12px;"></i> ${patient.current_visit.weight}kg</span>` : ''}
                                </small>
                            </div>
                        </div>
                    </div>
                `;
            }).join('');
            
            // Re-initialize handlers for new elements
            initializePatientHandlers();
            feather.replace();
        })
        .catch(error => {
            console.error('Error refreshing patient list:', error);
            document.getElementById('patientsList').innerHTML = '<p class="text-danger">Error loading patients</p>';
        });
}

// Add CSS for search results
const searchResultsCSS = `
<style>
.search-result-item {
    padding: 8px;
    border: 1px solid #4a5568;
    border-radius: 4px;
    margin-bottom: 4px;
    cursor: pointer;
    background-color: #2d3748;
    transition: background-color 0.2s;
}

.search-result-item:hover {
    background-color: #4a5568;
}

.patient-info-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
}

.info-item {
    margin-bottom: 0.5rem;
}

.info-item small {
    display: block;
    font-weight: 500;
}

.patient-actions {
    border-top: 1px solid #4a5568;
    padding-top: 1rem;
}

.patient-details h6 {
    color: #e2e8f0;
    font-weight: 600;
}
</style>
`;

// Add the CSS to the document head
if (!document.querySelector('#search-results-css')) {
    const style = document.createElement('style');
    style.id = 'search-results-css';
    style.innerHTML = searchResultsCSS;
    document.head.appendChild(style);
}