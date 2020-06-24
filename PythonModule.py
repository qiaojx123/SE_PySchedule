import json
import random
from operator import attrgetter
import courseDB
import requests

LESSON_ID = "id"
LESSON_TEACHERID = "teacher_ID"
LESSON_CAPACITY = "cap"
LESSON_DURATION = "length"

ROOM_ID = "id"
ROOM_CAPACITY = "size"

TEACHER_ID = "ID"
TEACHER_TIME = "teacher_time"

STATE_SUCCESS = "success"
STATE_INFO = "info"

MODIFY_COURSEID = "course_id"
MODIFY_TARGETTIME = "target_time"
MODIFY_ROOM = "classroom"

BASE_URL = "http://server.dydxh.cn:5000"

def Count1s(num):
	cnt = 0
	while num != 0:
		if num % 2 != 0: cnt+=1
		num = num//2
	return cnt

def GetLast1(num):
	if num == 0: return -1
	pos = 0
	while num%2!=1:
		num//=2;
		pos+=1
	return pos

class LessonInfo:
	__classID = 0
	__teacherID = 0
	__classTime = 0
	__length = 0
	__examTime = 0
	__position = 0
	capacity = 0

	def __init__(self):
		self.__classID = 0
		self.__teacherID = 0
		self.__classTime = 0
		self.__length = 0
		self.__examTime = 0
		self.__position = 0
		self.capacity = 0
		
	def FromJsonStr(self, jsonStr):
		data = json.loads(jsonStr)
		self.__classID = data[LESSON_ID]
		self.__teacherID = data[LESSON_TEACHERID]
		self.__length = data[LESSON_DURATION]
		self.capacity = data[LESSON_CAPACITY]
		return

	def FromJsonFile(self,pathStr):
		with open(pathStr,'r') as fin:
			buf = fin.read()
		self.FromJsonStr(buf)
		return

	def DebugOutput(self):
		print("Lesson ID: ", self.__classID)
		print("Teacher ID: ", self.__teacherID)
		print("Lesson Duration: ", self.__length)
		print("Lesson Time: ", self.__classTime)
		print("Lesson Capacity: ",self.capacity)
		print("Exam Time: ", self.__examTime)
		print("Position: ", self.__position)
		return

	def ModifyOutput(self):
		#jsonData = {LESSON_ID: self.__classID, LESSON_TEACHERID: self.__teacherID,
		#	 LESSON_POSITION: self.__position, LESSON_TIME: self.__classTime }
		jsonData = [self.__classID, self.__teacherID, self.__position, self.__classTime]
		return jsonData

	def SetClassTime(self, time): self.__classTime = time
	def SetPosition(self, position): self.__position = position
	def GetClassID(self): return self.__classID
	def GetTeacherID(self): return self.__teacherID
	def GetClassTime(self): return self.__classTime
	def GetLength(self): return self.__length
	def GetPosition(self): return self.__position
	def GetCapacity(self): return self.capacity

	def GetPeriods(self):
		if self.__length < 4: return 1
		if self.__length < 7: return 2
		return 3

	def ResetForSched(self):
		__classTime = 0
		__position = ""
		__examTime = 0
		return

class RoomInfo:
	__roomID = 0
	capacity = 0
	__useTime = 0

	def __init__(self):
		self.__roomID = 0
		self.capacity = 0
		self.__useTime = 0
		return

	def FromJsonStr(self, jsonStr):
		data = json.loads(jsonStr)
		self.__roomID = data[ROOM_ID]
		self.capacity = data[ROOM_CAPACITY]
		return

	def FromJsonFile(self, pathStr):
		with open(pathStr, 'r') as fin:
			buf = fin.read()
		self.FromJsonStr(buf)
		return

	def DebugOutput(self):
		print("Room ID: ", self.__roomID)
		print("Room Capacity: ", self.capacity)
		print("Room Time: ", self.__useTime)
		return

	def ModifyOutput(self):
		jsonData = {ROOM_ID: self.__roomID, ROOM_TIME: self.__useTime}
		return jsonData

	def AddUse(self,time):
		self.__useTime = self.__useTime | time
		return

	def GetRoomID(self):
		return self.__roomID

	def GetCapacity(self):
		return self.capacity

	def GetUseTime(self):
		return self.__useTime

	def SetUseTime(self, time):
		__useTime = time
		return

	def ResetForSched(self):
		self.__useTime = 0

class TeacherInfo:
	__ID = 0
	lessonCnt = 0
	__busyTime = 0
	lessons = []

	def __init__(self):
		self.__ID = 0
		self.lessonCnt = 0
		self.__busyTime = 0
		self.lessons = []
		
	def FromJsonStr(self, jsonStr):
		data = json.loads(jsonStr)
		self.__ID = data[TEACHER_ID]
		self.__busyTime = data[TEACHER_TIME]
		return

	def FromJsonFile(self, pathStr):
		with open(pathStr,'r') as fin:
			buf = fin.read()
		self.FromJsonStr(buf)
		return

	def AddLesson(self, lesson):
		self.lessons.append(lesson)
		self.lessonCnt += lesson.GetPeriods()
		return

	def GetID(self): return self.__ID
	def GetLessonCount(self): return self.lessonCnt
	def GetBusyTime(self): return self.__busyTime
	def SetID(self,ID): self.__ID=ID
	def SetBusyTime(self, time): self.__busyTime = time

	def OutputSchedule(self):
		print("Teacher ", self.__ID, ":")
		print("     一     二     三     四     五     六     日   ");
		sched = [[""]*14,[""]*14,[""]*14,[""]*14,[""]*14,[""]*14,[""]*14,[""]*14]

		for i in range(0,len(self.lessons)):
			ltime = self.lessons[i].GetClassTime();
			for j in range(1, 8):
				dtime = ltime & 0x1FFF
				p = GetLast1(dtime)
				while(p!=-1):
					sched[j][p+1] = "[{lesson:2}|{room:2}]".format(lesson=self.lessons[i].GetClassID(),room=self.lessons[i].GetPosition())
					dtime = dtime & ~(0x1<<p)
					p = GetLast1(dtime)
				ltime = ltime >> 13
				if ltime==0: break

		for i in range(1,14):
			print("{:2} ".format(i),end='')
			for j in range(1,8):
				if sched[j][i]=="" : print("[     ]",end='')
				else: print(sched[j][i],end='')
			print('')

		return

	def ModifyOutput(self):
		jsonData = {TEACHER_ID: self.__ID, TEACHER_TIME: self.__busyTime}
		return jsonData

	def GetLessonModify(self):
		res = []
		for i in range(len(self.lessons)): res.append(self.lessons[i].ModifyOutput())
		return res

	def ResetForSched(self): self.__busyTime=0

class RoomList:
	__useCount = [0]*8
	__rooms = []

	def __init__(self):
		self.__useCount=[0]*8
		self.__rooms=[]

	def __GetTimeMask(self,level,busytime):
		max1=0;max2=0;max3=0;max4=0
		pos1=0;pos2=0;pos3=0;pos4=0
		for i in range(1,8):
			if self.__useCount[i]>max1:
				max4=max3;pos4=pos3
				max3=max2;pos3=pos2
				max2=max1;pos2=pos1
				max1=self.__useCount[i]
				pos1=i
			elif self.__useCount[i]>max2:
				max4=max3;pos4=pos3
				max3=max2;pos3=pos2
				max2=self.__useCount[i]
				pos2=i
			elif self.__useCount[i]>max3:
				max4=max3;pos4=pos3
				max3=self.__useCount[i]
				pos3=i
			elif self.__useCount[i]>max4:
				max4=self.__useCount[i]
				pos4=i
		
		m1=0;m2=0;m3=0
		p1=0;p2=0;p3=0
		tmpMask = 0x545
		for i in range(1,8):
			n=Count1s(busytime&tmpMask)
			if n > m1:
				m3=m2;p3=p2
				m2=m1;p2=p1
				m1=n;p1=i
			elif n>m2:
				m3=m2;p3=p2
				m2=n;p2=i
			elif n>m3:
				m3=n;p3=i
			tmpMask = tmpMask<<13

		res = 0
		endDay = 5

		if level == 0:
			for i in range(endDay,0,-1):
				res=res<<13
				if i not in [pos1,pos2,pos3,pos4,p1,p2,p3]:
					res=res|0x3FF
		elif level == 1:
			for i in range(endDay,0,-1):
				res=res<<13
				if i not in [pos1,pos2,p1,p2]:
					res=res|0x3FF
		elif level == 2:
			for i in range(endDay,0,-1):
				res=res<<13
				if i not in [pos1,p1]:
					res=res|0x3FF
		elif level == 3:
			if m1 > len(self.__rooms) and random.random() < m1 / len(self.__rooms): endDay=7
			for i in range(endDay,0,-1): res=(res<<13)|0x3FF
		elif level == 4:
			if m1 > len(self.__rooms) and random.random() < m1 / len(self.__rooms): endDay=7
			for i in range(endDay,0,-1): res=(res<<13)|0x1FFF
		else:
			for i in range(7,0,-1): res=(res<<13)|0x1FFF

		return res

	def FromJsonStr(self,jsonStr):
		jsonData = json.loads(jsonStr)
		for i in range(len(jsonData)):
			tmp = RoomInfo()
			tmp.FromJsonStr(json.dumps(jsonData[i]))
			self.__rooms.append(tmp)
		return

	def FromJsonFile(self,pathStr):
		with open(pathStr,'r') as fin:
			buf = fin.read()
		self.FromJsonStr(buf)
		return

	def GetRoomModify(self):
		jsonData = []
		for i in range(0,len(self.__rooms)):
			jsonData.append(self.__rooms[i].ModifyOutput())
		return jsonData

	def Sort(self): self.__rooms.sort(key = attrgetter('capacity'))

	def FitInto(self, possibleTime, totalLen, relaxed):
		count3=0;count2=0
		slot3=0;slot2=0

		while totalLen>0:
			if totalLen>=5 or totalLen==3:
				totalLen-=3
				count3+=1
			else:
				totalLen-=2
				count2+=1
		tmpMask=0
		for i in range(1,8): tmpMask=(tmpMask << 13) | 0x848
		slotPos3=possibleTime&tmpMask
		slot3=Count1s(slotPos3)
		if slot3<count3: return 0
		tmpMask=0
		for i in range(1,8): tmpMask=(tmpMask << 13) | 0x101
		slotPos2=possibleTime&tmpMask
		slot2=Count1s(slotPos2)

		res=0

		if relaxed:
			if slot2 + slot3 - count3 < count2: return 0
			i=0
			for i in range(0,count2):
				p=GetLast1(slotPos2)
				if p==-1: break
				tmpRes = 0x3<<p
				res=res|tmpRes
				slotPos2=slotPos2&~tmpRes
			while i<count2:
				p = slotPos3.getLast1()
				tmpRes = 0x3 << (p-1)
				if p%13!=6: tmpRes = tmpRes<<1
				res = res|tmpRes
				slotPos3 = slotPos3&~tmpRes
				i+=1
			for i in range(0,count3):
				p=GetLast1(slotPos3)
				tmpRes = 0x7<<(p-1)
				res = res|tmpRes
				slotPos3 = slotPos3 & ~tmpRes
		else:
			if slot2<count2: return 0
			for i in range(0,count2):
				p=GetLast1(slotPos2)
				tmpRes = 0x3<<p
				res=res|tmpRes
				slotPos2=slotPos2&~tmpRes
			for i in range(0,count3):
				p=GetLast1(slotPos3)
				tmpRes = 0x7<<(p-1)
				res = res|tmpRes
				slotPos3 = slotPos3 & ~tmpRes
		return res

	def AllocRoomFor(self, busytime, totalLen, cap):
		for i in range(0,7):
			prioMask = self.__GetTimeMask(i,busytime)
			tmpMask = ~busytime & prioMask
			for j in range(0,len(self.__rooms)):
				if self.__rooms[j].GetCapacity() < cap: continue
				canAllocTime = ~self.__rooms[j].GetUseTime() & tmpMask
				allocRes = self.FitInto(canAllocTime, totalLen, i==6)
				if allocRes != 0:
					res = LessonInfo()
					res.SetClassTime(allocRes)
					res.SetPosition(self.__rooms[j].GetRoomID())
					self.__rooms[j].AddUse(allocRes)

					for k in range(1,7):
						self.__useCount[k] += Count1s(allocRes&0x545)
						allocRes = allocRes >> 13

					return res
		return LessonInfo()

	def ResetForSched(self):
		self.__useCount = [0]*8
		for i in range(len(self.__rooms)):
			self.__rooms[i].ResetForSched()

class Schedule:
	__rooms = RoomList()
	__teachers = []
	__isSuccess = False
	__config = {}

	def RoomsFromJsonFile(self, pathStr): self.__rooms.FromJsonFile(pathStr)
	def RoomsFromJsonStr(self, jsonStr): self.__rooms.FromJsonStr(jsonStr)

	def LessonsFromJsonStr(self, jsonStr):
		jsonData = json.loads(jsonStr)
		for i in range(len(jsonData)):
			tmpLesson = LessonInfo()
			tmpLesson.FromJsonStr(json.dumps(jsonData[i]))
			found = False
			for j in range(len(self.__teachers)):
				if self.__teachers[j].GetID() == tmpLesson.GetTeacherID():
					found = True
					break
			if found: self.__teachers[j].AddLesson(tmpLesson)
			else:
				tmpTeacher = TeacherInfo()
				tmpTeacher.AddLesson(tmpLesson)
				tmpTeacher.SetID(tmpLesson.GetTeacherID())
				self.__teachers.append(tmpTeacher)
		return

	def LessonsFromJsonFile(self, pathStr):
		with open(pathStr,'r') as fin:
			jsonData = fin.read()
		self.LessonsFromJsonStr(jsonData)
		return

	def GetLessonModify(self):
		res = []
		for i in range(len(self.__teachers)):
			res = res + self.__teachers[i].GetLessonModify()
		return res
	
	def GetTeacherModify(self):
		res = []
		for i in range(len(self.__teachers)):
			res.append(self.__teachers[i].ModifyOutput())
		return res
	
	def ResetForSched(self):
		self.__rooms.ResetForSched()
		for i in range(len(self.__teachers)): self.__teachers[i].ResetForSched()
		self.__isSuccess = False
		return

	def DoSchedule(self):
		if self.__initFail != True:
			self.ResetForSched()
			self.__teachers.sort(reverse = True, key = attrgetter('lessonCnt'))
			self.__rooms.Sort()

			for i in range(len(self.__teachers)):
				for j in range(len(self.__teachers[i].lessons)):
					tmpSche = self.__rooms.AllocRoomFor(self.__teachers[i].GetBusyTime(),self.__teachers[i].lessons[j].GetLength(), self.__teachers[i].lessons[j].GetCapacity());
					if tmpSche.GetClassTime()==0: return
					self.__teachers[i].lessons[j].SetPosition(tmpSche.GetPosition())
					self.__teachers[i].lessons[j].SetClassTime(tmpSche.GetClassTime())
					self.__teachers[i].SetBusyTime(self.__teachers[i].GetBusyTime()|tmpSche.GetClassTime())
			self.__isSuccess = True
		return

	def IsScheduleSuccess(self): return self.__isSuccess

	# return an object with success/fail info
	# write to database if success
	def OutputRes(self):
		if self.__initFail:
			res = {STATE_SUCCESS: False, STATE_INFO: self.__info}
		elif self.__isSuccess!=True:
			res = {STATE_SUCCESS: False, STATE_INFO: "Failed scheduling. If this continues happening, there may be too many lessons."}
		else:
			lessonModify = self.GetLessonModify()
			self.__db.insertArrangeData(lessonModify)
			res = {STATE_SUCCESS: True, STATE_INFO: "Succeed scheduling."}

		return res

	def DebugOutput(self):
		for i in range(len(self.__teachers)):
			self.__teachers[i].OutputSchedule()
		return
	
	# Takes a userid as parameter, return a object with whether success and info.
	# ret[STATE_SUCCESS] - whether the query is success
	# ret[STATE_INFO] - username when success, fail info when fail.
	def GetUserName(self, userid):
		ret = {STATE_SUCCESS:False,STATE_INFO:''}
		try:
			headers = {'token':self.__token,'magic':'sbsewcnm'}
			r = requests.get(BASE_URL+'/user/' + str(userid),headers=headers)
			if(r.status_code==500):
				raise Exception('User not exist.')
			if(r.status_code!=200):
				raise Exception('HTTP'+str(r.status_code))
			data = json.loads(r.text)
			ret[STATE_SUCCESS] = True
			ret[STATE_INFO] = data['username']
			return ret

		except Exception as e:
			ret[STATE_SUCCESS]=False
			ret[STATE_INFO]=str(e)
			return ret

	# Takes a courseid as parameter, return a object with whether success and info.
	# ret[STATE_SUCCESS] - whether the query is success
	# ret[STATE_INFO] - coursename when success, fail info when fail.
	def GetCourseName(self, courseid):
		ret = {STATE_SUCCESS:False,STATE_INFO:''}
		try:
			headers = {'token':self.__token,'magic':'sbsewcnm'}
			r = requests.get(BASE_URL+'/course/' + str(courseid),headers=headers)
			if(r.status_code==500):
				raise Exception('Course not exist.')
			if(r.status_code!=200):
				raise Exception('HTTP'+str(r.status_code))
			data = json.loads(r.text)
			ret[STATE_SUCCESS] = True
			ret[STATE_INFO] = data['name']
			return ret

		except Exception as e:
			ret[STATE_SUCCESS]=False
			ret[STATE_INFO]=str(e)
			return ret


	# token: The login token of basic group
	# db_config: an object for connecting to the db. view courseDB for detail.
	# server_url: the DB server's url.
	def __init__(self, token, db_config, server_url='http://localhost'):
		self.__rooms = RoomList()
		self.__teachers = []
		self.__isSuccess = False
		self.__token = token
		self.__initFail = False
		self.__info = ""
		try:
			self.__db = courseDB.course_arrange_db(db_config, server_url)
			#InitLessons
			#self.LessonsFromJsonFile("./autosched_lessons.json")
			headers = {'token':self.__token,'magic':'sbsewcnm'}
			r = requests.get(BASE_URL+'/course/all',headers=headers)

			response = json.loads(r.text)
			self.LessonsFromJsonStr(json.dumps(response))

			#InitRooms
			#return a list of objects
			classrooms = self.__db.queryClassroom()
			self.RoomsFromJsonStr(json.dumps(classrooms))
		except Exception as e:
			self.__initFail = True
			self.__info = str(e)
		else:
			self.__initFail = False
			self.__info = "Function Schedule is not called."
'''
class Modify:
	__targetTime = 0
	__isSuccess = False
	__info = "The modify func is not called."

	def DoModify(self):
		roomTime = self.__room.GetUseTime()
		curLessonTime = self.__lesson.GetClassTime()
		teacherTime = self.__teacher.GetBusyTime()

		roomTime = roomTime & ~curLessonTime
		teacherTime = teacherTime & ~curLessonTime

		if roomTime&self.__targetTime !=0:
			self.__info = "There are other lessons in the classroom on the target time."
			return
		elif teacherTime&self.__targetTime!=0:
			self.__info = "The teacher has other lessons on the target time."
			return
		elif Count1s(self.__targetTime)!=Count1s(curLessonTime):
			self.__info = "The lesson's length should not be changed."
			return

		self.__isSuccess = True
		self.__room.SetUseTime(roomTime|self.__targetTime)
		self.__lesson.SetClassTime(self.__targetTime)
		self.__teacher.SetBusyTime(teacherTime|self.__targetTime)
		return

	def OutputRes(self):
		if self.__isSuccess!=True:
			res = {STATE_SUCCESS : False, STATE_INFO : self.__info}
		else:
			roomModify = self.__room.ModifyOutput()
			lessonModify = self.__lesson.ModifyOutput()
			teacherModify = self.__teacher.ModifyOutput()
			res = {STATE_SUCCESS: True, STATE_INFO: "Succeed modifying", STATE_SINGLEROOM: roomModify,
				STATE_SINGLELESSON: lessonModify, STATE_SINGLETEACHER: teacherModify}
		return res
	
	# params should be a json or python object that includes:
	# MODIFY_COURSEID: integer //The id of the course to modify
	# MODIFY_TARGETTIME: integer(128bit) //The target time
	# MODIFY_ROOM: integer //The classroom's ID
	def __init__(self, params, db_config, server_url='http://localhost' ):
		try:
			self.__db = courseDB.course_arrange_db(db_config, server_url)
			self.__targetTime = params[MODIFY_TARGETTIME]
			self.__roomID = params[MODIFY_ROOM]
			self.__roomTime = self.__db.queryClassroomOccupiedTime(self.__roomID)
			self.__teacherTime = self.__db.queryTeacherOccupiedTime()

			__isSuccess = False
			__info = "The modify func is not called."

		except Exception as e:
			raise e
'''

headers = {'magic':'sbsewcnm'}
data = {'username': 'admin', 'password': '123456'}
r = requests.post(BASE_URL+'/login',headers=headers,json=data)
response = json.loads(r.text)
token = response['token']
db_config ={ "host":"localhost", "user":"root", "passwd":"root", "db":"resourcemanager"}

sched = Schedule(token,db_config,'http://localhost')
print(sched.GetUserName(1))
print(sched.GetCourseName(1))

sched.DoSchedule()
res = sched.OutputRes();
print(json.dumps(res))
sched.DebugOutput()

#params = {MODIFY_COURSEID:5,MODIFY_TARGETTIME:7392,MODIFY_ROOM:1}
#modify = Modify(params,db_config,'http://localhost')
#modify.DoModify()
#print(json.dumps(modify.OutputRes()))