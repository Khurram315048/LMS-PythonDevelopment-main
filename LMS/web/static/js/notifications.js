function displayFlashMessage(category, message) {
    let swalIcon = 'info';
    let swalTitle = 'Attention!';

    if (category === 'success') {
        swalIcon = 'success';
        swalTitle = 'Success!';
    }
    else if (category === 'warning') {
        swalIcon = 'warning';
        swalTitle = 'Warning';
    }
    else if (category === 'danger' || category === 'error') {
        swalIcon = 'error';
        swalTitle = 'Error';
    }

    Swal.fire({
        icon: swalIcon,
        title: swalTitle,
        text: message,
        confirmButtonColor: '#10367D',
        timer: 4000
    });
}

function confirmResultSubmission(formId) {
    Swal.fire({
        title: 'Are you sure?',
        text: "You can only generate this result once. Check all marks carefully!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#28a745',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Yes, Upload Now!',
        cancelButtonText: 'No, Cancel'
    }).then((result) => {
        if (result.isConfirmed) {
            document.getElementById(formId).submit();
        }
    });
}