document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  // By default, load the inbox
  load_mailbox('inbox');
});

// Uploads an email to the server
function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';

  // Upload an email to the server
  document.querySelector('#compose-form').onsubmit = function () {
    document.preventDefault;
    let recipients = document.querySelector('#compose-recipients').value;
    let subject = document.querySelector('#compose-subject').value;
    let body = document.querySelector('#compose-body').value;

    fetch('/emails', {
      method: 'POST',
      body: JSON.stringify({
      recipients: recipients,
      subject: subject,
      body: body
        })
      })
    .then(response => response.json())
    .then(result => {
      // Load mailbox
      localStorage.clear();
      load_mailbox('sent');
    });
    return false;
  }
}

// Loads requested mailbox
function load_mailbox(mailbox) {
  // Clear the storage to prevent use of an old response data
  localStorage.clear();

  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  // Fetch email from the server
  fetch(`/emails/${mailbox}`)
    .then(response => response.json())
    .then(emails => {

    // Display each email recived from the server
    emails.forEach((mail) => {
      createEmail(mailbox, mail);
    });
});
}

// Loads emails' details
function loadEmailDetails(mail) {

  // Mark the email as red
  toggleRed(mail.id, true);
  let emails = document.querySelector('#emails-view');

  // Clear the emails-view
  while (emails.lastElementChild) {
   emails.removeChild(emails.lastElementChild);
 }

  // Create container for an email
  let container = document.createElement('div');
  container.classList.add('p-4');

  // Create details about sender
  let sender = document.createElement('p');
  sender.innerHTML = `<b>From: </b> ${mail.sender}`;
  sender.classList.add('mb-2');
  container.append(sender);

  // Create details about recipient
  let recipients = document.createElement('p');
  recipients.innerHTML = `<b>To: </b> ${mail.recipients}`;
  recipients.classList.add('mb-2');
  container.append(recipients);

  // Create details about subject
  let subject = document.createElement('p');
  subject.innerHTML = `<b>Subject: </b>  ${mail.subject}`;
  subject.classList.add('mb-2');
  container.append(subject);

  // Create details about time
  let timestamp = document.createElement('p');
  timestamp.innerHTML = `<b>Timestamp: </b>  ${mail.timestamp}`;
  timestamp.classList.add('mb-2');
  container.append(timestamp);

  // Create button to reply
  let reply = document.createElement('button');
  reply.classList.add('btn', 'btn-sm', 'btn-outline-primary', 'mr-2', 'reply');
  reply.innerText = 'Reply';
  reply.addEventListener('click', function() {

    // Load an email form
    compose_email();

    // Add Re: prefix if it is first reply
    let subject = mail.subject;
    if (subject.slice(0, 3) !== 'Re:'){
      subject = 'Re: ' + subject;
    }

    // Prefill the form
    document.querySelector('#compose-recipients').value = mail.sender;
    document.querySelector('#compose-subject').value = subject;
    document.querySelector('#compose-body').value = `\n \n \n \n On ${mail.timestamp} ${mail.sender} wrote: \n "${mail.body}"\n`;
  });
  container.append(reply);

  // Create a horizontal line
  let hr = document.createElement('hr');
  container.append(hr);

  // Create details about the content
  let body = document.createElement('p');
  body.innerHTML = mail.body;
  body.classList.add('my-3');
  container.append(body);

  // Display created email
  emails.append(container);
  }

// Creates an email
function createEmail(mailbox, mail) {

  // Create container for an email
  let container = document.createElement('div');
  container.classList.add('border', 'border-secondary', 'p-1', 'd-flex', 'align-items-center', 'my-3');
  container.id = mail.id;

  // Add background color
  if (mail.read){
    container.style.backgroundColor = '#e5e5e5';
    }
  else {
    container.style.backgroundColor = 'white';
  }

  // Add sender and title
  let leftBox = document.createElement('div');
  leftBox.classList.add('email', 'flex-grow-1', 'd-flex', 'mx-3');
  let leftSpan = document.createElement('span');
  leftSpan.innerHTML = `<b>${mail.sender}</b> ${mail.subject}`;
  leftBox.append(leftSpan);

  // Add timestamp
  let rightSpan = document.createElement('span');
  rightSpan.classList.add('text-muted', 'ml-auto');
  rightSpan.innerHTML = mail.timestamp;
  leftBox.append(rightSpan);
  container.append(leftBox);

  // Add archive/unarchive button
  if (mailbox !== 'sent'){
    if (mail.archived){

      // Create button to unarchive an email
      let unarchive = document.createElement('button');
      unarchive.classList.add('btn', 'btn-link', 'mr-2', 'unarchive', 'ml-auto');
      unarchive.innerText = 'unarchive';
      unarchive.addEventListener('click', function () {
        localStorage.clear();
        // Unarchive the email
        toggleArchive(this.parentElement.id, false);
      });
      container.append(unarchive);
    }
    else {

      // Create button to archive an email
      let archive = document.createElement('button');
      archive.classList.add('btn', 'btn-link', 'mr-2', 'archive', 'ml-auto');
      archive.innerText = 'archive';
      archive.addEventListener('click', function () {

        // Archive the email
        toggleArchive(this.parentElement.id, true);
      });
      container.append(archive);
    }
  }

  // Add event listener to load email's details
  leftBox.addEventListener('click', () => loadEmailDetails(mail, mailbox));
  document.querySelector('#emails-view').append(container);
}

// Toggles emails' archived attribute and loads mailbox
function toggleArchive(id, bool) {

  // Toggle emails archive atribut
  fetch(`/emails/${id}`, {
  method: 'PUT',
  body: JSON.stringify({
      archived: bool
    })
  })
  .then(() => {
      load_mailbox('inbox');
  });
}

// Marks an email as red
function toggleRed(id, bool) {

  // Mark the email as red
  fetch(`/emails/${id}`, {
    method: 'PUT',
    body: JSON.stringify({
    read: bool
    })
  })
}
