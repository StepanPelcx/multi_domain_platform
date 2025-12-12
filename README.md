Student Name: [Stepan Pelc]
Student ID: [M01087679]
Course: CST1510 -CW2 - Multi-Domain Intelligence Platform

## Project Description

This project represents an application with three main domains (Cyber Security, Datasets Metadata, IT Tickets). The user can do all of the CRUD functions or analyze the samples by graphs on each of the domains. All of these domains contain AI assistants for chating and also analyzing the samples from the database. The application also contains an authentification of the user. Each user has to register or login. They can check their password strength, or choose their role. The authentification system includes password hashing all the other functions for the user verification.

## Features

- Secure password hashing using bcrypt with automatic salt generation
- User registration with duplicate username prevention
- User login with password verification
- Input validation for usernames and passwords
- File-based user data persistence
- Check password strength function
- Change password function
- See your role function
- CRUD functions for (Cyber Incidents, Datasets Metadata, IT Tickets)
- Analyzis of the database tables (Cyber Security, Datasets Metadata, IT Tickets)
- AI assistant for all the tables (Cyber Security, Datasets Metadata, IT Tickets)
- AI analyzer for all the tables (Cyber Security, Datasets Metadata, IT Tickets)
- For "Admin" users, they can access other users data.

## Technical Implementation

- Hashing Algorithm: bcrypt with automatic salting
- Data Storage: Plain text file (`users.txt`) with comma-separated values
- Password Security: One-way hashing, no plaintext storage
- Validation: Username (3-20 alphanumeric characters), Password (8-24 characters)
- Dependencies: pandas
                streamlit
                openai
                numpy
                datetime
                pathlib
                matplotlib
                sqlite3
                secrets
                bcrypt
                re
- Installation: To install all of the dependencies, go to the CMD (windows)/terminal(mac)
                and type pip install LibraryName / pip3 install LibraryName
Python version: Python 3.13.7
File Structure: 

