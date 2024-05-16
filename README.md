# Mini Amazon System

Spring 2024 Duke CompSci516 Standard Project

## Project Overview

In this project, you will build a miniature version of Amazon. On this website, sellers can create product listings and an inventory of products for sale. Users can browse and purchase products. Transactions are conducted within the website using virtual currency. Users can review products and sellers who fulfill their orders.

Link to the final project long demo video: - https://drive.google.com/file/d/1P1HTYG8H7shJtt73JRQm73MqhLgoBkUm/view?usp=sharing - https://www.youtube.com/watch?v=3ZUkjsGLn2A
Link to the additional short video (extras): - https://drive.google.com/file/d/1uKkhCZFhpQsn5nM0_-4PM0uK9g1LOG5a/view?usp=sharing - https://www.youtube.com/watch?v=STP-SKlkeUo

## Running/Stopping the Website

To run the website, in Duke OIT container shell, go into the repository
directory and issue the following commands:

```
poetry shell
flask run
```

The first command ensures that you are in the correct Python virtual
environment managed by a tool called `poetry` (you can tell that your
command-line prompt looks differently --- it would start with the name
of the environment). The second command runs the Flask/web server.
Do NOT run Flask outside the `poetry` environment; you will get
errors.

To stop your app, type <kbd>CTRL</kbd>-<kbd>C</kbd> in the container
shell; that will take you back to the command-line prompt, still
inside the `poetry` environment. If you are all done with this app for
now, you can type `exit` to get out of the `poetry` environment and
get back to the normal container shell.
