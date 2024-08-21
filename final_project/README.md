### Requirements
https://cs50.harvard.edu/web/2020/projects/final/capstone/

### How to run your application
I used django 3.2.25. Last recomended python version for this version of django is python3.10. I installed python3.10 and its venv globally. Then I created venv using python3.10, activated venv and I installed 	requirements.txt.

### Project description
There are 3 groups of users which can use the app:
1. Unlogged users can search db for books, see book details and read reviews.
2. Logged in users can login/logout, borrow/renew books, see currently borrowed books and history of borrowings, 	change password, review books, see profile details, send, compose and receive emails.
3. Staff members have full access to the db. They can register users, delete/update user's accounts (including their own account), they can accept/reject user requests, return books. On the main dashboard (home page) they can see users' requests for books, all lent books, overdue books, filter accounts of all users.They are also regular users which means they can borrow books.Application automatically calculates fees. Staff member must confirm that the fee was paid back.



