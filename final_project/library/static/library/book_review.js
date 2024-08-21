document.addEventListener('DOMContentLoaded', function() {
  const reviewFormLink = document.querySelector('#reviewFormLink');
  const reviewForm = document.querySelector('#reviewForm');
  const bookPk = document.querySelector('#data').dataset.bookpk;

  // Review form is only shown for logged in users
  if (reviewFormLink) {
    reviewFormLink.addEventListener('click', function(e) {
      e.preventDefault();

      // Show the form
      if (reviewForm.classList.contains('d-none')) {
        reviewForm.classList.remove('d-none');
        reviewForm.classList.add('d-block');
        reviewFormLink.innerHTML = 'Hide the add review form';

      // Hide the form
      } else {
        reviewForm.classList.remove('d-block');
        reviewForm.classList.add('d-none');
        reviewFormLink.innerHTML = 'Show the add review form';
      }
    });
  }
  // By default, load book reviews
  loadReviews(bookPk);

  // Add event listener to the form
  if (reviewForm) {
    reviewForm.addEventListener('submit', function(e) {
      e.preventDefault();
      closeAlert();
      let content = reviewForm.content.value;

      // Create error message if there is no review content
      if (content === '') {
        createAlert('Enter your review!', 'danger')

      // Submit review
      } else {
        postReview({content: content, bookPk:bookPk});
      }
    });
  }

});


function loadReviews(bookPk) {
  fetch(`/load/reviews/${bookPk}/`)
  .then(response => {
    if (response.status === 200){
      return response.json();
    }
    else {
      return Promise.reject(`Something went wrong! Http status: ${response.status} ${response.text}`);
    }
  })
  .then(data => {
    // For each received review create box and append it to reviews container
    let reviewContainer = document.querySelector('#reviewContainer');
    data.forEach((i) => {
      let review = createReview(i);
      reviewContainer.appendChild(review);
    });
    })
  .catch((error) => {
    console.log(error);
    createAlert(error, 'danger');
    });
  }

function delReview(data) {
  fetch('/del/review/', {
    method: 'POST',
    body: JSON.stringify(data),
    headers: {
      'Content-Type': 'application/json',
      "X-CSRFToken": getCookie("csrftoken"),
    }
    })
  .then(response => {
    closeAlert();
    if (response.status === 200){
      return data;
    }
    else {
      return Promise.reject(`Something went wrong! Http status: ${response.status} ${response.text}`);
    }
  })
  .then(data => {
    // Remove review
    let review = document.querySelector(`#pk${data.id}`);
    review.remove();
    })
  .catch((error) => {
    createAlert(error, 'danger');
    });
  }

function postReview(data) {
  fetch('/add/review/', {
    method: 'POST',
    body: JSON.stringify(data),
    headers: {
      'Content-Type': 'application/json',
      "X-CSRFToken": getCookie("csrftoken"),
    }
    })
  .then(response => {
    closeAlert();
    if (response.status === 200){
      return response.json();
    }
    else {
      return Promise.reject(`Something went wrong! Http status: ${response.status} ${response.text}`);
    }
  })
  .then(data => {
    let container = document.querySelector('#reviewContainer');
    let review = createReview(data);

    // The newest reviews are displayed at the top of the container
    if (container.firstElementChild) {
      container.insertBefore(review, container.firstElementChild);
    } else {
      container.appendChild(review);
    }

    // Clear the form textarea
    let submitTextArea = document.querySelector('#reviewForm');
    submitTextArea.content.value = '';
    })
  .catch((error) => {
    createAlert(error, 'danger');
    console.log(error);
    });
  }

function editReview(data) {
  fetch('/edit/review/', {
    method: 'POST',
    body: JSON.stringify(data),
    headers: {
      'Content-Type': 'application/json',
      "X-CSRFToken": getCookie("csrftoken")
    }
    })
  .then(response => {
    closeAlert();
    if (response.status === 200){
      return response.json();
    }
    else {
      return Promise.reject(`Something went wrong! Http status: ${response.status} ${response.text}`);
    }
  })
  .then(data => {
    // Replace old review with new one
    let currentReview = document.querySelector(`#pk${data.id}`);
    let nextReview = document.querySelector(`#pk${data.id}`).nextElementSibling;
    let editedReview = createReview(data);
    let reviewContainer = document.querySelector('#reviewContainer');
    currentReview.remove();
    reviewContainer.insertBefore(editedReview, nextReview);
    })
  .catch((error) => {
    createAlert(error, 'danger');
    });
  }

function createReview(data) {
  // Create container
  let container = document.createElement('div');
  container.id = 'pk' + data.id;
  container.classList.add('bg-white', 'my-3', 'p-3', 'shadow');

  //Create title
  let title = document.createElement('small');

  // Create link to the review author and add it to the title
  let link = document.createElement('a');
  let dataObj = document.querySelector('#data');
  link.href = `/users/profile/${data.author_id}/`
  link.innerHTML = data.author__username;
  let span = document.createElement('span');
  let creationDate = new Date(data.creation_date);
  span.innerHTML = ' on ' + creationDate.toLocaleString('en-us', {dateStyle:'medium', timeStyle:'short'});
  title.appendChild(link);
  title.appendChild(span);

  // Create content
  let content = document.createElement('p');
  content.classList.add('my-2')
  content.innerHTML = data.content;

  // Create edit button
  let editBtn = document.createElement('a');
  editBtn.classList.add('ms-2', 'text-success', 'fw-bold')
  editBtn.innerHTML = 'EDIT';
  editBtn.href = '';
  editBtn.addEventListener('click', function(e) {
    e.preventDefault();
    let editForm = editBtn.nextElementSibling;

    // If edit form is already displayed - remove it
    if (editForm) {
      editForm.remove();

    // Otherwise create edit form
    } else {
      let editBlock = createEditBlock(data);
      this.parentElement.appendChild(editBlock);
    }
  });

  // Create delete button
  let delBtn = document.createElement('a');
  delBtn.classList.add('text-danger', 'fw-bold');
  delBtn.innerHTML = 'DEL';
  delBtn.href = '';
  delBtn.addEventListener('click', function(e) {
    e.preventDefault();
    delReview(data);
  });
  container.appendChild(title);
  container.appendChild(content);
  let userPk = document.querySelector('#data').dataset.userpk;

  // Display del and edit buttons only for authors of the reviews
  if (data.author_id.toString() === userPk) {
    container.appendChild(delBtn);
    container.appendChild(editBtn);
  }
  return container;
}

function createEditBlock(data) {
  // Create container
  let container = document.createElement('div');
  container.classList.add('px-5', 'py-3');

  // Create textarea
  let textarea = document.createElement('textarea');
  textarea.classList.add('block', 'w-100', 'form-control');
  textarea.value = data.content;

  // Create submit button
  let submit = document.createElement('input');
  submit.type = 'submit';
  submit.classList.add('block', 'w-100', 'btn', 'btn-outline-success', 'mt-2');
  submit.value = 'Edit review';

  // Add event listener to edit review
  submit.addEventListener('click', function(e) {
    let content = textarea.value;
    data.content = content;
    editReview(data);
  });
  container.appendChild(textarea);
  container.appendChild(submit);
  return container;
}
