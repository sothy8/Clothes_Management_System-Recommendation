function validateForm() {
    const height = document.getElementById('id_height').value;
    const weight = document.getElementById('id_weight').value;
    if (height <= 0 || weight <= 0) {
        alert('Height and weight must be positive numbers.');
        return false;
    }
    return true;
}