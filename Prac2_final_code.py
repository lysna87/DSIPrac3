from dataclasses import dataclass
from datetime import datetime

class CalendarManager:
    # tests are expexting 2 inputs.
    def __init__(self, calendarAccessor):
        self.calendar = calendarAccessor

    def createMeeting(self, description, startTime, attendeeNames):
        meetingId = self.calendar.createMeeting(description, startTime, attendeeNames)
        return meetingId

    def findNextMeeting(self, name):
        meetingInfo = self.calendar.findNextMeeting(name)
        return meetingInfo

class InMemoryCalendarAccessor:

    def __init__(self):
        self.calendar = InMemoryCalendar()

    def createMeeting(self, description, startTime, attendeeNames):
        meeting = self.calendar.createMeeting(description, startTime, attendeeNames)
        return meeting.getId()

    def findNextMeeting(self, name):
        meeting = self.calendar.findNextMeeting(name)
        return self._getMeetingInfo(meeting) if meeting is not None else None

    def _getMeetingInfo(self, meeting):
        mInfo = MeetingInfo(meeting.getId(), meeting.getDescription(), meeting.getStartTime())
        return mInfo

@dataclass
class MeetingInfo:
    id: int
    description: str
    startTime: datetime

    def __repr__(self):
        return f"Meeting {self.id} \"{self.description}\" at {self.startTime}"

class InMemoryCalendar:

    def __init__(self):
        self.meetings = []

    def createMeeting(self, description, startTime, attendeeNames):
        meeting = Meeting(description, startTime, attendeeNames)
        self.addMeeting(meeting)
        return meeting

    def addMeeting(self, meeting):
        self.meetings.append(meeting)

    def findNextMeeting(self, name):
        meeting = self.findMeeting(lambda m: m.includesAttendeeNamed(name))
        return meeting

    def findMeeting(self, predicate):
        for meeting in self.meetings:
            if predicate(meeting):
                return meeting
        return None

class UniqueIdGenerator:

    def __init__(self):
        self.prevId = 0

    def next(self):
        self.prevId += 1
        return self.prevId

class Meeting:

    idGenerator = UniqueIdGenerator()

    def __init__(self, description, startTime, attendeeNames=None):
        if not attendeeNames:
            raise ValueError("Meeting must have one or more " \
            "attendees")
        #changed code to ensure a value error.
        self.id = self.idGenerator.next()
        self.description = description
        self.attendees = [self._createAttendee(name) for name in attendeeNames or list()]
        self.startTime = startTime

    def _createAttendee(self, name):
        return Contact(name)

    def getId(self):
        return self.id

    def getDescription(self):
        return self.description

    def getStartTime(self):
        return self.startTime

    def includesAttendeeNamed(self, name):
        for contact in self.attendees:
            if contact.getName() == name:
                return True
        return False

    def __repr__(self):
        attendeeNames = ",".join(map(str,self.attendees))
        return f"Meeting {self.id} description: {self.description} starting: {self.startTime} attendees: {attendeeNames}"

class Contact:

    def __init__(self, name):
        self.name = name

    def getName(self):
        return self.name

    def __repr__(self):
        return self.name

def createDummyMeetings(manager):
    manager.createMeeting("First Meeting", datetime(2021,5,17,9,10), ["Wolfgang"])
    manager.createMeeting("Second Meeting", datetime(2021,5,17,11,10), ["Wolfgang","Mei","Matt"])
    manager.createMeeting("Third Meeting", datetime(2021,5,17,14,10), ["Matt"])

def testFindMeeting(manager):
    nextMeetingInfo = manager.findNextMeeting("Matt")
    print("The next meeting with Matt is:")
    print(nextMeetingInfo)

def main():
    manager = CalendarManager()
    createDummyMeetings(manager)
    testFindMeeting(manager)

if __name__ == "__main__":
    main()
