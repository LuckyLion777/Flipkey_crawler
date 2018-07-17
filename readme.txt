There are several files for this scraper.

1) Install Python2.7

2) Python Modules(requirements.txt)
-In requirements.txt, there are modules which I used for this program.
-You should install those modules first.
-Open terminal and enter commands like this:

$cd <the path of this directory>
$sudo pip install -r requirements.txt

3) You can run "flipkey_crawler.py" file on console.This is just a program file.

$cd <the path of this directory>
$python ./flipkey_crawler.py   
Or
$python ./flipkey_crawler.py -f 1 -t 114638
Or
$python ./flipkey_crawler.py --viewfrom 7 --viewto 100

Note: If you don't input arguments, crawler will scrape user from 1 to 114638.

4) There is "log.txt" file and you can view the log.

5) There is "result.csv" and this is the result csv file.
This csv file contains following fields and these are the fields which you required.

View No	: User No
Page URL : Page URL for this user
           http://www.flipkey.com/frontdesk/view/<View No>/	
Number Of Properties : the number of properties
Company Website	: the companmy website (if it exists on the page)
Company FacebookPage : the company facebook page (if it exists on the page)
Company PhoneNumber : the company phone number
Location Of Company/User : the location of the company/user
Badge Container Properties: 	The badges at the top are also very important.. 
				because it tells us the type of user that they are...
				"Accepts FlipKey Payments", "Property Owner", etc
Number Of Reviews : the number of reviews the property has had	
TopText : the text in the paragraph tag "badges" at the top
