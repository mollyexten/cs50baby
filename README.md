# This is CS50 Baby # 
An application for recording a baby's sleeping habits.
View a walkthrough [here](https://www.youtube.com/watch?v=yfLQD_pZjPs&t=1s).

## Description ##
I was inspired to create this web application after my experience with a really precise baby sleep tracker. I thought it was cumbersome to enter the exact time my baby fell asleep and woke up, so I created a tracker that worked with rough estimates.
With CS50 Baby, parents can understand their baby's sleep habits without getting a headache.

## Contents ##
In application.py, I use Flask to create different webpages for CS50 Baby: 
* /register
* /login
* /(index)
* /naps
* /overnight 
* /apology
The routes for these different webpages use Python to get input from the user and check it against, insert into, and select from the sleep database.
These routes work with the templates in the templates folder.

## Use ##
A user of CS50 Baby can register and log in to their account to view a log of naps and overnight sleep starting with the most recently recorded date.
The nav bar includes two pages: naps and overnight.

### Naps ###
In the naps page the user can record the length of up to three naps (measured in minutes)
These nap times will be inserted into the sleep database.
Clicking submit will redirect the user to the index with the newly recorded naps in the log.

### Overnight ###
In the overnight page, the user can record the baby's bedtime and wakeup time along with information on how often and for how long the baby woke up in the middle of the night.
These overnight times will be inserted into the sleep database.
Clicking submit will redirect the user to the index with the newly recorded overnight sleep in the log.

### Index ###
The index displays the information from the sleep database organized by most recent date.

