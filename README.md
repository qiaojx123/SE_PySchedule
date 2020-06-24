# SE_PySchedule
ZJU software engeering scheduling - in python

## Note
**You can always change the json's key by editing the global vars at the beginning of the python file.**

**All classes contains methods for reading from both file and string.**

## Auto Scheduling
### Init the Schedule class:

    autosched = Schedule(token,db_config,'http://localhost')

- The first parameter token is for visiting the base-info group's api. The token is generated when the user logged in.
- The second parameter db_config is the config used for connecting database.
- The third parameter is the url used for visiting database. Get more detailed info from database api.

For example, the three token can be initialized as:

    #Get token
    headers = {'magic':'sbsewcnm'}
    data = {'username': 'admin', 'password': '123456'}
    r = requests.post(BASE_URL+'/login',headers=headers,json=data)
    response = json.loads(r.text)
    token = response['token']
    
    #db_config
    db_config ={ "host":"localhost", "user":"root", "passwd":"root", "db":"resourcemanager"}
    
    #url
    url = "http://localhost"
    
### Auto scheduling
Call function DoSchedule:

    autosched.DoSchedule()

This will try to automatically schedule the courses.

AFTER THIS, call OutputRes() to write the data into database and get the infomation whether the scheduling process is success.

    res = autosched.OutputRes()
    #res[STATE_SUCCESS] - True or False, whether the scheduling is successful
    #res[STATE_INFO] - 'Succeed scheduling.' or the reason of failing.
    
Note that writing back to database is done in OutputRes() and need no other function call.
### Get username or coursename
AFTER INITIALIZING THE CLASS:

    userRes = autosched.GetUserName(1)
    #userRes[STATE_SUCCESS] - True or False, whether successful
    #userRes[STATE_INFO] - string, username when success, fail info when fail
    
    courseRes = autosched.GetCourseName(1)
    #courseRes[STATE_SUCCESS] - True or False, whether successful
    #courseRes[STATE_INFO] - string, coursename when success, fail info when fail
## Modifying
Directly use the database's api to do modify.
