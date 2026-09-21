# LECTURE 02

## Problem 01
![alt text](Problem_01.png)
Figure 1.1: The return status codes are 201, 200. The initial list BOOKS is a empty list, I use method POST to add 2 new books into it. After that I use method GET to get all the book in the list.


![alt text](Problem_01-1.png)
Figure 1.2: The return status codes are 422, 400, and 415. To get the status code 422 UNPROCESSABLE ENTITY, I pass the data unsufficiently (without the title field). To get the status code 400 BAD REQUEST, I pass the data with an invalid JSON format. And to get the status code 415 UNSUPPORTED MEDIA TYPE, i don't pass the Content-Type.

## Problem 02
![alt text](Problem_02.png)
Figure 2.1: Using POST method to add 2 books into BOOKS.

![alt text](Problem_02-1.png)
Figure 2.2: Using PUT, PATCH, DELETE methods. Note that in the example about using PUT method, the passed data only includes 2 fields author and title. Therefore other fields will be set to null value. And if the method DELETE succeed, the return status code is 204 NO CONTENT.