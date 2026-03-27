document.addEventListener('DOMContentLoaded', function() {
  const borrowBtn = document.querySelector('#borrowBtn');
  const renewBtn = document.querySelector('#renewBtn');
  const alertContainer = document.querySelector('#alertContainer');

  // By default, add event listener if borrow button is a available
  if (borrowBtn) {
    borrowBtn.addEventListener('click', function(e) {
      let pk = borrowBtn.dataset.pk;
      borrowBook({pk: pk}, alertContainer);
    });
  }

  // By default, add event listener if renew button is available
  if (renewBtn) {
    renewBtn.addEventListener('click', function(e) {
      let pk = renewBtn.dataset.pk;
      renewBook({pk: pk}, alertContainer);
    });
  }
});

function renewBook(data, alertContainer) {
  fetch('/renew/book/', {
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
    if (data.flag === 'ok') {
      createAlert(data.message, 'success');
      // Hide renew button
      let renewBtn = document.querySelector('#renewBtn');
      renewBtn.classList.add('d-none');
      let displayBox = document.querySelector('#loanInfo');

      // Update return date
      let returnDate = displayBox.firstElementChild.nextElementSibling.lastChild;
      let newDate = new Date(data.return_date);
      returnDate.textContent = newDate.toLocaleString('en-us', {dateStyle:'medium'});

      // Update can renew information
      let canRenewInfo = displayBox.lastElementChild.lastChild;
      canRenewInfo.textContent = 'Already renewed';

    } else {
      createAlert(data.message, 'danger');
    }
  })
  .catch((error) => {
    console.log(error);
    createAlert(error, 'danger');
  })
}

function borrowBook(data, alertContainer) {
  fetch('/borrow/book/', {
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
    if (data.flag === 'ok') {
      // Hide borrow button
      let borrowBtn = document.querySelector('#borrowBtn');
      borrowBtn.classList.add('d-none');

      // Display accept button
      let acceptBtn = document.querySelector('#acceptBtn');
      if (acceptBtn) {
        acceptBtn.classList.remove('d-none');
      }

      let displayBox = document.querySelector('#loanInfo');

      // Clear the display box
      while (displayBox.firstElementChild ) {
        displayBox.firstElementChild.remove();
      }

      // Create link to book owner
      let statusContainer = document.createElement('p');
      let statusDescription = document.createElement('small');
      statusDescription.classList.add('me-3', 'text-muted');
      statusDescription.innerHTML = 'Status:';
      statusContainer.append(statusDescription);
      statusContainer.append('pending');

      // If user is staff member create link to the loan
      if (data.loan_pk) {
        let loanContainer = document.createElement('p');
        let loanDescription = document.createElement('small');
        loanDescription.classList.add('me-3', 'text-muted');
        loanDescription.innerHTML = 'Request:';
        let loanLink = document.createElement('a');
        loanLink.href = `/loan/details/${data.loan_pk}/`;
        loanLink.innerHTML = 'click me';
        loanContainer.appendChild(loanDescription);
        loanContainer.appendChild(loanLink);
        displayBox.append(loanContainer);
      }
      displayBox.append(statusContainer);
      createAlert(data.message, 'success');
    } else {
      createAlert(data.message, 'danger');
    }
  })
  .catch((error) => {
    console.log(error);
    createAlert(error, 'danger');
  })
}
