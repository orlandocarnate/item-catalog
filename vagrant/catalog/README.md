# Catalog - Udacity
### Full Stack Web Development ND

## About
A long time ago I created a static jewelry website for my sister-in-law and I thought I could apply what I learned and create a data-driven site with CRUD functions using Python, Flask, SQLAlchemy, and Bootstrap.
This is Jewelry Catalog application provides:
* a list of items within a variety of categories
* a user registration and authentication system
* Registered users will have the ability to:
    * CReate new items
    * Update items
    * Delete items
* Only the original creator of an item can edit or delete it.

## Getting Started
These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites
You will need to install these software:
* Download and Install **[Python 3](https://www.python.org/downloads/)**
* Download and Install **[Vagrant](https://www.vagrantup.com/downloads.html)**
* Download and Install **[VirtualBox 3](https://www.virtualbox.org/wiki/Downloads)**
* Clone or Download the Github repository at 
    **(https://github.com/orlandocarnate/fullstack-nanodegree-vm)** 
    in your vagrant folder.
* You will need to provide your own `client_secrets` for the Google API ad Facebook API
* Create and download your Google API key at **[Google Developers](https://developers.google.com/)**
* Create and download your Facebook API key at **[Facebook for Developers](https://developers.facebook.com/)**


## Start the virtual machine
From your terminal, inside the *vagrant* subdirectory, run the command `vagrant up`. This will cause Vagrant to download the Linux operating system and install it. When `vagrant up` is finished running, you will get your shell prompt back. At this point, you can run `vagrant ssh` to log in to your newly installed Linux VM. If the shell prompt starts with the word `vagrant` then you are loggied into Linux VM.

## Run the Python Web Server
Make sure you're in the `vagrant/catalog` folder within the Linux VM terminal. Enter 'ls' to see a list of items within the vagrant folder. You should see `project.py`.

In the Linux VM terminal run this command:
`python project.py`

## Log In using Google or Facebook
If you have a Google or Facebook account you can click on the login button on the top right Nav Bar. This will take you to the OAUTH page. After successfully logging in you will be able to createm edit or delete items or modify the Category description. The login button will change into a log


## Template Style with Bootstrap
I probably spent half the time researching Bootstrap for my Flask templates. Below are some of the sites I have been researhing:
* **[GetBootstrap.com Examples](http://getbootstrap.com/docs/4.1/examples/)**
* **[Tooplate.com Shelf Template](https://www.tooplate.com/live/2092-shelf)**
* **[W3schools.com Clothing Store Template](https://www.w3schools.com/w3css/tryw3css_templates_clothing_store.htm)**
* **[Startbootstrap.com Shop Homepage Template](https://startbootstrap.com/template-overviews/shop-homepage/)**
