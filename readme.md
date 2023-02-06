# Warning
This project is educational.
# About the project
The project is a service for sending non-modifiable messages. Each saved message is hashed and its hash is part of the page address.

The hash is formed as follows:

`sha512((title + message + created_time).encode('ascii')).hexdigest()`

On the message reading page, there is a hash of the page and its address, the data is compared on the server, but you can compare them yourself using the function indicated above.
# Installation
1. To install, just run `pip install -r requirements.txt`

2. The first registered user is the application administrator. He has access to all messages sent by users, as well as a list of users.
