# CoWin Notifier

Cowin Notifier is a python script that can find available slots for vaccination in India. It uses Cowin's open APIs to find slots based on choices such as - Vaccination, Age and Pin Code

# Installation

To use the script, ensure that a version of Python 3 is installed.
Post this, run the following command to install the required dependencies:
```bash
pip install -r requirements.txt
```

All other dependencies are available upon installing python.

# How to use
Download the .zip file and extract it to any folder on your computer.

To use the tool, all you need to do is run the Cowin_notifier.py.
It'll ask you a series of questions to search for slots according to your preference.

To get the district ID, go to:https://www.cowin.gov.in/home.

Right-click on an empty space in your browser and choose 'Inspect'.

Click on the Network tab on the top of the menu that just opened.

Now, in the Cowin portal, choose the district for which you wish to obtain information and click search.

There will now be a new addition to the network tab.

Click on that addition, scroll to the end and you will be able to obtain your district ID


# Upcoming changes

Enabling users to obtain the district ID from the script.

Updating the sound used for notification.

Enabling users to log in and book slots automatically.