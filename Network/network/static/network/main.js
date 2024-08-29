document.addEventListener('DOMContentLoaded', function(e) {

  // Toggles following
  const toggleFollowing = document.querySelectorAll('.toggle')[0];
  if (toggleFollowing){
    toggleFollowing.onclick = function(){
      toggle(this.dataset.requested_profile);
    }
  }

  // Updates post likes
  document.querySelectorAll('.fa-thumbs-up').forEach((link) => {
    link.onclick = function() {
    closeAlert();
    let parent = this.parentElement;
    like(this.dataset.post, 'like', parent);
   }
  });

  // Updates post unlikes
  document.querySelectorAll('.fa-thumbs-down').forEach((link) => {
    link.onclick = function() {
    closeAlert();
    let parent = this.parentElement;
    like(this.dataset.post, 'unlike', parent);
   }
  });

  // Edits a post
  document.querySelectorAll('.edit').forEach((link) => {
    link.onclick = function (event) {
      event.preventDefault();

      // Close displayed alerts
      closeAlert();
      let postContent = this.previousElementSibling.innerText;
      let postBody = this.parentElement;
      let container = postBody.parentElement;

      // Display edit box
      container.insertBefore(createEditBox(postContent, postBody.id), postBody);

      // Hide old post
      container.lastElementChild.classList.add('d-none');
  }
});


// Connects server and updates the like count
function like(post, type, parent) {
  fetch(`/like/?post=${post}&type=${type}`)
  .then(x => x.json())
  .then(y => {
    if ((y.likes != undefined) && (y.unlikes != undefined)){
      parent.children[1].innerHTML = y.likes;
      parent.children[4].innerHTML = y.unlikes;
    }

    // Display message if returned
    if (y.message !== ''){
      createAlert(y.message, parent);
    }
  })
  .catch(error => 'Error!');
}

// Lets the user toggle whether or not follow another's user posts
function toggle(requested_profile) {
  fetch(`/toggle/?requested_profile=${requested_profile}`)
  .then(x => x.text())
  .then(y => {

    // Updates the number of followers
    document.querySelector('#followers').innerHTML = y;

    // Renames the link
    if (toggleFollowing.innerHTML == 'Follow'){
      toggleFollowing.innerHTML = 'Unfollow';
    }
    else {
      toggleFollowing.innerHTML = 'Follow';
    }
  });
}

// Creates and displays alert
function createAlert(message, parent) {
  let div = document.createElement('div');
  div.classList.add('alert', 'alert-info', 'alert-dismissible');
  div.innerHTML =  `<button type="button" class="close" \
  data-dismiss="alert">&times;</button><strong>Info!</strong> ${message}`;
  let node = parent.children[0];
  parent.insertBefore(div, node);
}

// Closes previeosly displayed alerts
function closeAlert() {
  document.querySelectorAll('button.close').forEach((alert) => {
    alert.click();
  });
}

// Creates post edit box
function createEditBox(postContent, pk) {
  let editBoxContainer = document.createElement('div');
  let textArea = document.createElement('textArea');
  let saveButton = document.createElement('button');
  let cancelButton = document.createElement('button');
  editBoxContainer.classList.add('form-group');
  textArea.classList.add('form-control','w-100', 'mt-3', 'mb-2');
  textArea.value = postContent;
  cancelButton.innerText = 'Cancel';
  saveButton.innerText = 'Save';
  saveButton.classList.add('button', 'btn', 'btn-primary', 'mr-2');
  cancelButton.classList.add('button', 'btn', 'btn-primary', 'mr-2');
  editBoxContainer.append(textArea);
  editBoxContainer.append(cancelButton);
  editBoxContainer.append(saveButton);
  let postBody = document.getElementById(pk);

  // Removes the edit box
  cancelButton.onclick = function () {
    postBody.classList.remove('d-none');
    editBoxContainer.remove();
  }

  // Updates content of the post
  saveButton.onclick = function () {

    // Get the id of the post and the edited content
    let content = this.parentElement.firstElementChild.value;
    let pk = this.parentElement.nextElementSibling.id;
    let data = {content: content, pk: pk};

    // Send data to the server
    putEditData(data);

    // Remove edit box
    editBoxContainer.remove();
  }
  return editBoxContainer;
}

// Connects server and saves edited post content
function putEditData(data) {
  fetch('/edit/', {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      "X-CSRFToken": getCookie("csrftoken"),
    },
    body: JSON.stringify(data),
    })
  .then(response => {
    let postBody = document.getElementById(data.pk);
    if (response.ok){

      // Replace the old content with edited one
      postBody.firstElementChild.innerText = data.content;

      // Show the post
      postBody.classList.remove('d-none');
    }
    else{

      // Create alert
      createAlert('Something went wrong! Try again!', postBody);

      // Show the post
      postBody.classList.remove('d-none');
    }
  })
  .catch((error) => {
    createAlert(error, postBody);
    });
  }

// Gets csrftoken from cookies
function getCookie(name) {
    var dc = document.cookie;
    var prefix = name + "=";
    var begin = dc.indexOf("; " + prefix);
    if (begin == -1) {
        begin = dc.indexOf(prefix);
        if (begin != 0) return null;
    }
    else
    {
        begin += 2;
        var end = document.cookie.indexOf(";", begin);
        if (end == -1) {
        end = dc.length;
        }
    }
    return decodeURI(dc.substring(begin + prefix.length, end));
}
});
