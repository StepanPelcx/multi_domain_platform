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
- Data Storage: Database with four tables ("users", "cyber_incidents", "datasets_metadata", "it_tickets") with comma-separated values 
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
- Python version: Python 3.13.7

## Running the application

Application File Structure: 
                multi_domain_platform/
                    .streamlit/
                        secrets.toml
                    database/
                        cyber_incidents.csv
                        datasets_metadata.csv
                        intelligent_platform.db
                        it_tickets.csv
                    images/
                        datasets.jpg
                        header.jpg
                        security.jpg
                        tickets.jpg
                    models/
                        __init__.py
                        dataset.py
                        it_ticket.py
                        security_incident.py
                        user.py
                    pages/
                        1_Home_Hub.py
                        2_Cyber_Security.py
                        3_Datasets_Metadata.py
                        4_IT_Tickets.py
                        5_Settings.py
                    services/
                        __init__.py
                        ai_assistant.py
                        auth_manager.py
                        database_manager.py
                    __init__.py
                    .gitignore
                    Home.py
                    README.md
                    requirements.txt

How to run:
    To run this application you need to have downloaded these .jpg files: 
    datasets.jpg - https://cdn.prod.website-files.com/6391b5b30283a58cafb3bb77/66e466d438ac6f24eaef108b_top-10-datasets-images-2024-imp.webp
    security.jpg - https://media.istockphoto.com/id/1412282189/photo/lock-network-technology-concept.jpg?s=612x612&w=0&k=20&c=hripuxLs9pS_7Ln6YWQR-Ow2_-BU5RdQ4vOY8s1q1iQ=
    tickets.py - https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTCktiF2Ms8dafZIeIQGRM53xXnHkH5XiJ5YQ&s
    header.jpg - https://miro.medium.com/v2/resize:fit:1200/0*dBvqE3AFe08f9H6i.jpg
    And place them into images folder.

    To access the local web page, you then need to have the whole application file structure ready, according to the structure above. The page is accessible only by running the Home.py file. 
    When you run this file you just need to type: streamlit run "path to the Home.py file"
    The other way is to open CMD or terminal and type: streamlit run "path to the Home.py file"
    If you followed the instructions correctly, the web page should open for you.
