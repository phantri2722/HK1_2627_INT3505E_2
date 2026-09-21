# HOMEWORK 02
Find a public API and list 5 endpoints - indicate the method, status code, headers, RESTful or not

## BASE URL: https://api.github.com

##  Get a user
- Endpoint: /users/{username}
- Method: GET
- Status Code:
    + 200 OK
    + 404 Not Found
- Headers:
    + Accept: appication/vnd.github+json
    + X-GitHub-Api-Version: 2026-03-10
- RESTful: Yes 

##  Get a repository
- Endpoint: /repos/{owner}/{repo}
- Method: GET
- Status Code:
    + 200 OK
    + 404 Not Found
    + 301 Moved Permanently
    + 403 Forbidden
- Headers:
    + Accept: application/vnd.github+json
    + Authorization: Bearer <TOKEN>
    + X-GitHub-Api-Version: 2026-03-10
- RESTful: Yes 

## Endpoint: /repos/{owner}/{repo}/issues
- Method: GET
- Status Code:
    + 200 OK
    + 404 Not Found
    + 301 Moved Permanently
    + 422
- Headers:
    + Accept: application/vnd.github+json
    + Authorization: Bearer <TOKEN>
    + X-GitHub-Api-Version: 2026-03-10
- RESTful: Yes 

## Endpoint: /repos/{owner}/{repo}/issues/{issue_number}/comments
- Method: POST
- Status Code:
    + 201 Created
    + 403
    + 404
    + 410
    + 422
- Headers:
    + Accept: application/vnd.github+json
    + Authorization: Bearer <TOKEN>
    + X-GitHub-Api-Version: 2026-03-10
- RESTful: Yes 

## Endpoint: /repos/{owner}/{repo}/issues/comments/{comment_id}
- Method: DELETE
- Status Code:
    + 204 No Content
- Headers:
    + Accept: application/vnd.github+json
    + Authorization: Bearer <TOKEN>
    + X-GitHub-Api-Version: 2026-03-10
- RESTful: Yes 