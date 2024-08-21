document.addEventListener('DOMContentLoaded', function(e) {
  const allUsersBtn = document.querySelector('#allUsersBtn');
  const pendingRequestsBtn = document.querySelector('#pendingRequestsBtn');
  const overdueLoansBtn = document.querySelector('#overdueLoansBtn');
  const loansBtn = document.querySelector('#loansBtn');
  const alertContainer = document.querySelector('#alertContainer');
  const loansContainer = document.querySelector('#loansContainer');
  const usersContainer = document.querySelector('#usersContainer');
  const usersBlock = document.querySelector('#usersBlock');
  const overdueBlock = document.querySelector('#overdueBlock');
  const pendingRequestsBlock = document.querySelector('#pendingRequestsBlock');
  const loansBlock = document.querySelector('#loansBlock');
  if (usersContainer) {
    // By default, load list of all users
    loadItems({parameter:''}, createUserItem, usersContainer);

    // Update list of users
    const userFilterForm = document.querySelector('#userFilterForm');
    userFilterForm.addEventListener('keyup', function(e) {
      let query = userFilterForm.value;
      loadItems({parameter:query}, createUserItem, usersContainer);
    });
  }

  // REGULAR USERS

  // Create items for none staff users
  if (loansContainer) {
    // Load items and sort it by return date
    loadItems({parameter:'return_date'}, createLoanItem, loansContainer);
    const bookTitleBtn = document.querySelector('#bookTitleBtn');
    const statusBtn = document.querySelector('#statusBtn');
    const returnDateBtn = document.querySelector('#returnDateBtn');

    // Set up default sort parameters
    var bookTitle = 'book';
    var status= 'status';
    var returnDate = '-return_date';

    // Add eventListener to sort items by book title
    bookTitleBtn.addEventListener('click', function(e) {
      let data = {parameter: bookTitle};
      loadItems(data, createLoanItem, loansContainer);

      // Toggle the ascending/descending ordering
      if (bookTitle === 'book') {
        bookTitle = '-book';
      } else {
        bookTitle = 'book';
      }

      // Set the active button and hide the others
      BtnsClearActiveState('user_dashboard_btn');
      bookTitleBtn.classList.add('active');
    });

    // Add eventListener to sort items by loan status
    statusBtn.addEventListener('click', function(e) {
      let data = {parameter: status};
      loadItems(data, createLoanItem, loansContainer);

      // Toggle the ascending/descending ordering
      if (status=== 'status') {
        status= '-status';
      } else {
        status= 'status';
      }

      // Set the active button and hide the others
      BtnsClearActiveState('user_dashboard_btn');
      statusBtn.classList.add('active');
    });

    // Add eventListener to sort items by return date
    returnDateBtn.addEventListener('click', function(e) {
      let data = {parameter: returnDate};
      loadItems(data, createLoanItem, loansContainer);

      // Switch the ascending/descending ordering
      if (returnDate === 'return_date') {
        returnDate = '-return_date';
      } else {
        returnDate = 'return_date';
      }

      // Set the active button and hide the others
      BtnsClearActiveState('user_dashboard_btn');
      returnDateBtn.classList.add('active');
    });
    }

  // STAFF MEMBERS

  // Display pending request for staff members
  if (pendingRequestsBtn) {
    pendingRequestsBtn.addEventListener('click', function(e) {
      // Set the active button and hide the others
      BtnsClearActiveState('staff_dashboard_btn');
      pendingRequestsBtn.classList.add('active');

      // Display the container and hide the others
      usersBlock.classList.add('d-none');
      pendingRequestsBlock.classList.remove('d-none');
      overdueBlock.classList.add('d-none');
      loansBlock.classList.add('d-none');
    });
  }

  // Display all users for staff members
  if (allUsersBtn) {
    allUsersBtn.addEventListener('click', function(e) {
      // Set the active button and hide the others
      BtnsClearActiveState('staff_dashboard_btn');
      allUsersBtn.classList.add('active');

      // Display the container and hide the others
      usersBlock.classList.remove('d-none');
      pendingRequestsBlock.classList.add('d-none');
      overdueBlock.classList.add('d-none');
      loansBlock.classList.add('d-none');
    });
  }

  // Display overdue loans for staff members
  if (overdueLoansBtn) {
    overdueLoansBtn.addEventListener('click', function(e) {
      // Set the active button and hide the others
      BtnsClearActiveState('staff_dashboard_btn');
      overdueLoansBtn.classList.add('active');

      // Display the container and hide the others
      usersBlock.classList.add('d-none');
      pendingRequestsBlock.classList.add('d-none');
      overdueBlock.classList.remove('d-none');
      loansBlock.classList.add('d-none');
    });
  }

  // Display all loans for staff members
  if (loansBtn) {
    loansBtn.addEventListener('click', function(e) {
      // Set the active button and hide the others
      BtnsClearActiveState('staff_dashboard_btn');
      loansBtn.classList.add('active');

      // Display the container and hide the others
      usersBlock.classList.add('d-none');
      pendingRequestsBlock.classList.add('d-none');
      overdueBlock.classList.add('d-none');
      loansBlock.classList.remove('d-none');
    });
  }
  });

// Create user item to display in staff member dashbord
function createUserItem(obj) {
    // Create container
    let wrapper = document.createElement('div');
    wrapper.classList.add('shadowItem', 'shadow', 'py-3', 'py-md-1', 'text-center');

    // Row is a link to user's profile
    let row = document.createElement('div');
    row.addEventListener('click', function(e) {
      location.href = '/users/profile/' + obj.user_pk;
    });
    row.classList.add('row');

    // Create columns for: username, number of borrowed books, last login and email address
    for (var i in obj) {
      if (obj.hasOwnProperty(i)) {
        if (i !== 'user_pk') {
          let col = document.createElement('div');
          col.classList.add('col-md-3');
          let p = document.createElement('p');
          p.classList.add('p-2');
          p.classList.add('m-0');
          if (i === 'last_login') {
            let lastLogin = new Date(obj[i]);
            p.innerHTML = lastLogin.toDateString();
          } else {
            p.innerHTML = obj[i];
          }
          col.appendChild(p);
          row.appendChild(col);
          wrapper.appendChild(row);
        }
      }
    }
    return wrapper;
  }

// Create loan item to display it in none staff member dashbord
function createLoanItem(data) {
  // Create loan item container
  let wrapper = document.createElement('div');
  wrapper.classList.add('shadowItem', 'shadow', 'py-3', 'py-md-1', 'text-center');
  let row = document.createElement('div');
  if (data.is_overdue) {
    wrapper.classList.add('bgOverdue');
  }
  row.classList.add('row');

  row.addEventListener('click', function(e) {
    location.href = '/loan/details/' + data.loan_pk;
  });

  // Create book title column
  let col1 = document.createElement('div');
  col1.classList.add('col-md-4');
  let p1 = document.createElement('p');
  p1.classList.add('p-2');
  p1.classList.add('m-0');
  p1.innerHTML = data.book_title;
  col1.appendChild(p1);

  // Create loan status column
  let col2 = document.createElement('div');
  col2.classList.add('col-md-4');
  let p2 = document.createElement('p');
  p2.classList.add('p-2');
  p2.classList.add('m-0');
  p2.innerHTML = data.status;
  col2.appendChild(p2);

  // Create return date column
  let col3 = document.createElement('div');
  col3.classList.add('col-md-4');
  let p3 = document.createElement('p');
  p3.classList.add('p-2');
  p3.classList.add('m-0');

  // For pending requests don't display return dates
  if (data.return_date) {
    let date = new Date(data.return_date);
    p3.innerHTML = date.toLocaleString('en-us', {dateStyle:'medium'});
  } else {
    p3.innerHTML = '-';
  }
  col3.appendChild(p3);

  // Append columns to the container
  row.appendChild(col1);
  row.appendChild(col2);
  row.appendChild(col3);
  wrapper.appendChild(row);
  return wrapper;
}

function loadItems(data, f, container) {
  fetch(('/'), {
    method: 'POST',
    body: JSON.stringify(data),
    headers: {
      'Content-Type': 'application/json',
      "X-CSRFToken": getCookie("csrftoken"),
    }
    })
  .then(response => {
    if (response.status === 200){
      return response.json();
    }
    else {
      return Promise.reject(`Something went wrong! Http status: ${response.status} ${response.text}`);
    }
  })
  .then(data => {
    while (container.firstElementChild) {
      container.firstElementChild.remove();
    }
    data.data.forEach((i) => {
      let item = f(i);
      container.appendChild(item);
    });
    })
  .catch((error) => {
    createAlert(error, alertContainer, 'danger');
    })
  }

  // Remove active class from a group of buttons
function BtnsClearActiveState(btnClass) {
  let buttons = document.querySelectorAll('.' + btnClass);
  for (let btn of buttons) {
    btn.classList.remove("active");
  }
}
