document.addEventListener('DOMContentLoaded', function(e) {
  const historyContainer = document.querySelector('#historyContainer');
  const userPk = document.querySelector('#userPk').dataset.userpk;
  const url = `/users/profile/${userPk}/`;

  // By default, set item counter to 0 and flag allItemsLoaded to true
  var counter = 0;
  var allItemsLoaded = true;

  // By default load first 5 items
  let data = {start:counter};
  loadItems(data, historyContainer, url);


window.addEventListener('scroll', function(e) {

    // If user reaches bottom of the page load 5 more items
    if (window.scrollY + window.innerHeight >= document.documentElement.scrollHeight) {

      // Check if all items were loaded
      if (!allItemsLoaded) {

        // Set flag allItemsLoaded to true to ensure that new request won't be posted until last one is finished
        allItemsLoaded = true;
        let data = {start: counter};
        loadItems(data, historyContainer, url);
      }
    }
  });

// Posts data, displays items, increments counter and sets flag allItemsLoaded
function loadItems(data, container, url) {
  fetch((url), {
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
    if (data.response) {

      // Display all received items
      data.response.forEach((i) => {
        let item = createLoanItem(i);
        container.appendChild(item);
      });

      // Increment counter
      counter += 5;

      // Set allItemsLoaded flag to false
      allItemsLoaded = false;
    }
    else {
      // If server returned none set allItemsLoaded flag to true
      allItemsLoaded = true;
    }
    })
  .catch((error) => {
    console.log(error);
    createAlert(error, 'danger');
    })
  }

// Creates row with 6 column and fills them with provided data
function createLoanItem(data) {
  // Create container
  let wrapper = document.createElement('div');
  wrapper.classList.add('shadow', 'py-3', 'py-md-1', 'text-center');
  let row = document.createElement('div');
  row.classList.add('row');

  // Create column for book title
  let col1 = document.createElement('div');
  col1.classList.add('col-md-3');
  let p1 = document.createElement('p');
  p1.classList.add('p-2','m-0');
  let bookLink = document.createElement('a');
  bookLink.href = `/book/details/${data.book_pk}/`
  bookLink.innerHTML = data.book_title;
  p1.appendChild(bookLink);
  col1.appendChild(p1);

  // Create column for book author
  let col2 = document.createElement('div');
  col2.classList.add('col-md-2');
  let p2 = document.createElement('p');
  p2.classList.add('p-2','m-0');
  p2.innerHTML = data.book_author;
  col2.appendChild(p2);

  // Create column for loan date
  let col3 = document.createElement('div');
  col3.classList.add('col-md-2');
  let p3 = document.createElement('p');
  p3.classList.add('p-2','m-0');
  if (data.loan_date) {
    let loanDate = new Date(data.loan_date);
    p3.innerText = loanDate.toLocaleString('en-us', {dateStyle:'medium'});
  } else {
    p3.innerText = '-';
  }
  col3.appendChild(p3);

  // Create column for return date
  let col4 = document.createElement('div');
  col4.classList.add('col-md-2');
  let p4 = document.createElement('p');
  p4.classList.add('p-2','m-0');
  if (data.return_date) {
    let date = new Date(data.return_date);
    p4.innerHTML = date.toLocaleString('en-us', {dateStyle:'medium'});
  } else {
    p4.innerHTML = '-';
  }
  col4.appendChild(p4);

  // Create column for request status
  let col5 = document.createElement('div');
  col5.classList.add('col-md-2');
  let p5 = document.createElement('p');
  p5.classList.add('p-2','m-0');
  p5.innerHTML = data.status;
  col5.appendChild(p5);

  // Create column for link to details
  let col6 = document.createElement('div');
  col6.classList.add('col-md-1');
  let p6 = document.createElement('p');
  p6.classList.add('p-2','m-0');
  let loanLink = document.createElement('a');
  loanLink.href = `/history/details/${data.loan_pk}/`
  loanLink.innerHTML = '<small>details</small>';
  p6.appendChild(loanLink);
  col6.appendChild(p6);
  row.appendChild(col1);
  row.appendChild(col2);
  row.appendChild(col3);
  row.appendChild(col4);
  row.appendChild(col5);
  row.appendChild(col6);
  wrapper.appendChild(row);
  return wrapper;
}
});
