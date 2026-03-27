document.addEventListener('DOMContentLoaded', function(e) {
  document.querySelectorAll('.shadowItem').forEach((book) => {
    book.addEventListener('click', function(e) {
      location.href = "/book/details/" + book.id;
    });
  });
});
