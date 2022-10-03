

# Local Set Up

1. Clone the repository:
    ```
    git clone https://github.com/dmcconeghy/cl-backend-assessment.git 
    ```

2. Move to the project directory:
    ```
    cd cl-backendassessment 
    ```

3. Pull the Docker image for this project:
    ```
    docker pull dmcconeghy/cl-pythonapp-image
    ```

3. Run the image:
    ```
    docker run dmcconeghy/cl-pythonapp-image
    ```

4. Docker Compose the containers:
    ``` 
    docker compose up -d db
    docker compose up --build pythonapp 
    ```

Visiting the server locally at http://127.0.0.1 should return: `Ground Control to Major Tom`

# Using the API:

This project has a flask webserver with a psql database integrated through SQLAlchemy. 
Once your instance is running, you can interact with the API in the following ways:

## 1. Create USERS by POST request to (http://127.0.0.1/api/users)
   - The Users table accepts the following required data:
     - Name (string)
     - Email (string, unique)
     - Address (string)
     - Image (url/string)
   - E.g., A valid query might look like: 
```
http://127.0.0.1/api/users?name=dave&email=dave%40email.com&address=126%20maple%20lane&image=pictureofme.com/image.jpg
```
   - This should return "User created Name: dave, Email: dave@email.com, Address: 126 maple lane, Image: pictureofme.com"
   - Invalid inputs (missing any field) return a 404, unless the field contains a duplicate email, which returns "A user with that email already exists."
   - Each user id is unique and generated automatically. 

## 2. Manipulate USERS entries with GET, PATCH or DELETE requests as follows:
   - (http://127.0.0.1/api/users/<user_id>) to DELETE or GET. 
   - http://127.0.0.1/api/users/<user_id>) as PATCH with parameters name, email, address, and/or image. Unused parameters will remain unchanged.
     - E.g., A valid PATCH for user id #1 would be 
```
http://127.0.0.1/api/users/1?name=David 
```

## 3. Search for USERS by name, email or address, using SQL partial pattern matching. 
```
http://127.0.0.1/api/users/search/name?name=David
``` 
 - Returns Name: David, Email: dave@email.com, Address: 126 maple lane, Image: pictureofme.com/image
 - Similarly, see `http://127.0.0.1/api/users/search/address` or `http://127.0.0.1/api/users/search/email`

## 4. Create AUDIO DATA for users using the following JSON format:
```
{
    "user_id": 1,
    "ticks": [-66.33, -66.33, -63.47, -69.03999999999999, -84.61, -80.18, -75.75, -71.32, -66.89, -62.46, -58.03, -53.6, -49.17, -44.74, -40.31], 
    "selected_tick": 5, 
    "session_id": 3333, 
    "step_count": 0 
} 
```

 - Audio data must be passed with a `user_id`. 
 - `ticks` is an array of exactly 15 numbers, each of which range from -10.0 to -100.0
 - `selected_tick` must be between 0 and 14
 - `session_ids` are unique across all users. 
 - `step_count` is unique per session and must range between 0 and 9. 

A valid POST query using CURL would look like this: 

```
curl --request POST \
--url http://127.0.0.1/api/audio \
--header 'Content-Type: application/json' \
    --data '{"user_id": 1,
"ticks": [-66.33, -66.33, -63.47, -69.03999999999999, -84.61, -80.18, -75.75, -71.32, -66.89, -62.46, -58.03, -53.6, -49.17, -44.74, -40.31], "selected_tick": 5, "session_id": 3333, "step_count": 0
}'
```

## 5. AUDIO DATA handles GET and PATCH queries:
 - Any audio can be retrieved/searched for using its `session_id` as in:
   -  `http://127.0.0.1:5000/api/audio/session/3333` which returns "Here's the session: Session ID: 3455, User ID: 5, Selected Tick: 5, Step Count: 0, Ticks: [-96.33, -96.33, -93.47, -89.03999999999999, -84.61, -80.18, -75.75, -71.32, -66.89, -62.46, -58.03, -53.6, -49.17, -44.74, -40.31]"
 - To update AUDIO DATA, we can modify the `step_count`, `selected_tick`, and `ticks`. Note that presently `ticks` must be modified as a group of 15 which, if validated, will replace the previous version.
 - Additionally, if we want to request ALL of a particular user's audio session data, then we can perform that request as follows: `http://127.0.0.1/api/audio/<user_id>`.  

# Testing this project