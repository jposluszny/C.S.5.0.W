// Creates and displays alert
function createAlert(message, type) {
  // Select container for alert
  let alertContainer = document.querySelector('#alertContainer');

  // If the alert type is danger change the header to error
  var messageHeader = type;
  if (type === 'danger'){
    messageHeader = 'Error';
  }

  // Create and style alert
  let alert = document.createElement('div');
  alert.classList.add('alert', `alert-${type}`, 'alert-dismissible');
  alert.innerHTML =  `<button type="button" class="close" \
  data-dismiss="alert">&times;</button><strong>${messageHeader.toUpperCase()}!</strong> ${message}`;

  // Append alert
  alertContainer.appendChild(alert);
}

// Removes previously displayed alerts
function closeAlert() {
  let alertContainer = document.querySelector('#alertContainer');
  while (alertContainer.firstElementChild) {
    alertContainer.firstElementChild.remove();
  }
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
