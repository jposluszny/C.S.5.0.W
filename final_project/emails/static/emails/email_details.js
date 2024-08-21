document.addEventListener('DOMContentLoaded', function() {
  const archiveBtn = document.querySelector('#archiveBtn');
  const unarchiveBtn = document.querySelector('#unarchiveBtn');

  archiveBtn.addEventListener('click', function(e) {
    let emailpk = archiveBtn.dataset.emailpk;
    archiveEmail({emailpk: emailpk});
  });

  unarchiveBtn.addEventListener('click', function(e) {
    let emailpk = unarchiveBtn.dataset.emailpk;
    unarchiveEmail({emailpk: emailpk});
  });

});

// Connects server and changes archived attribute to true, hides archive button and shows unarchived button
function archiveEmail(data) {
  fetch('/email/update/email/archive/', {
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

      // Hide archive button
      let archiveBtn = document.querySelector('#archiveBtn');
      archiveBtn.classList.add('d-none');

      // Display unarchive button
      let unarchiveBtn = document.querySelector('#unarchiveBtn');
      unarchiveBtn.classList.remove('d-none');

      // Change archived to true
      let archivedInfo = document.querySelector('#archivedInfo');
      archivedInfo.innerHTML = 'True';
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

// Connects server and changes archived attribute to false, hides unarchive button and shows archived button
function unarchiveEmail(data) {
    fetch('/email/update/email/unarchive/', {
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

        // Hide the unarchive button
        let unarchiveBtn = document.querySelector('#unarchiveBtn');
        unarchiveBtn.classList.add('d-none');

        // Display the unarchive button
        let archiveBtn = document.querySelector('#archiveBtn');
        archiveBtn.classList.remove('d-none');

        // Change archived to false
        let archivedInfo = document.querySelector('#archivedInfo');
        archivedInfo.innerHTML = 'False';
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
