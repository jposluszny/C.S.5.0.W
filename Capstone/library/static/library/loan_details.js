document.addEventListener('DOMContentLoaded', function() {
  const acceptBtn = document.querySelector('#acceptBtn');
  const rejectBtn = document.querySelector('#rejectBtn');

  if (acceptBtn) {
    acceptBtn.addEventListener('click', function(e) {
      let bookpk = acceptBtn.dataset.bookpk;
      acceptRequest({bookpk: bookpk}, container);
    });
  }

  if (rejectBtn) {
    rejectBtn.addEventListener('click', function(e) {
      let bookpk = rejectBtn.dataset.bookpk;
      let rejectForm = document.querySelector('#rejectForm');
      if (rejectForm.classList.contains('d-none')) {

        // Show reject form
        rejectForm.classList.remove('d-none');
      } else {

        // Hide reject form
        rejectForm.classList.add('d-none');
      }
    });
  }
});

// Connects server and marks request as accepted
function acceptRequest(data, container) {
  fetch('/accept/request/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      "X-CSRFToken": getCookie("csrftoken"),
    },
    body: JSON.stringify(data),
    })
  .then(response => {
    closeAlert();
    if (response.status === 200){
      return response.json();
    }
    else {
      return Promise.reject(`Http status: ${response.status} ${response.statusText}`);
    }
  })
  .then(data => {
    if (data.flag === 'OK'){
      createAlert(data.message, 'success');
      // Hide borrow button
      let acceptBtn = document.querySelector('#acceptBtn');
      acceptBtn.classList.add('d-none');

      // Hide reject request button
      let rejectBtn = document.querySelector('#rejectBtn');
      rejectBtn.classList.add('d-none');

      // Display return book button
      let returnBtn = document.querySelector('#returnBtn');
      returnBtn.classList.remove('d-none');

      // Change status to "accepted"
      let status = document.querySelector('#status');
      status.innerHTML = 'accepted';

      // Enter loan date
      let loanDate = document.querySelector('#loanDate');
      let loanDateObj = new Date(data.loan_date);
      loanDate.innerHTML =  loanDateObj.toLocaleString('en-us', {dateStyle:'medium'});

      // Enter return date
      let returnDate = document.querySelector('#returnDate');
      let returnDateObj = new Date(data.return_date);
      returnDate.innerHTML = returnDateObj.toLocaleString('en-us', {dateStyle:'medium'});
    }
    else {
      createAlert(data.message, 'danger');
    }
  })
  .catch((error) => {
    console.log(error);
    createAlert(error, 'danger');
  })
  }
