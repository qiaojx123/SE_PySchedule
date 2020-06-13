# SE_PySchedule
ZJU software engeering scheduling - in python

## Note
**You can always change the json's key by editing the global vars at the beginning of the python file.**

## Auto Scheduling
Use class Schedule like this:

    sched = Schedule()
    sched.LessonsFromJsonFile("./autosched_lessons.json")
    sched.RoomsFromJsonFile("./autosched_rooms.json")
    sched.DoSchedule()
    print(json.dumps(sched.OutputRes()))
    #sched.DebugOutput()

The sched.OutputRes() will return a key-value object which can be directly dump into json.

This contains a value with key "success" indicating whether it succeeded or failed, and "info" indicating the success or error info.

And it also contains three arries named by default as "rooms", "lessons" and "teachers", which contains the data need to be changed in the database.

## Modifying
Use class Modify like this:

    modify = Modify()
    modify.RoomFromJsonFile("./modify_room.json")
    modify.LessonFromJsonFile("./modify_lesson.json")
    modify.TeacherFromJsonFile("./modify_teacher.json")
    modify.TargetTimeFromJsonFile("./modify_time.json")

    modify.DoModify()
    print(json.dumps(modify.OutputRes()))

The modify.OutputRes() will return a key-value object which can be directly dump into json.

This contains a value with key "success" indicating whether it succeeded or failed, and "info" indicating the success or error info.

And it also contains three arries named by default as "room", "lesson" and "teacher", which contains the data need to be changed in the database. **Note that these keys are different from that in auto scheduling whose keys are in plural form.**
