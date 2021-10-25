# Author: Wolfgang Mayer, University of South Australia, 2021
# License: CC BY https://creativecommons.org/licenses/by/4.0/

# Import stuff
from dataclasses import dataclass
from datetime import datetime
from unittest.mock import Mock
import pytest

###################################################################################################
# Introduction                                                                                    #
###################################################################################################

# This project implements a simple calendar application that maintains a searchable calendar containing
# meetings. Meetings are associated with attendees.
#
# Requires python >=3.6 and pytest
#
# To run, execute `python main.py` or run the `pytest` tests
#
# The architecture uses layers to separate Client application, Business logic, Resource Abstractions
# and Data Stores.
#
# Currently, the data store is in memory.
# The only calendar functions that are currently implemented are to create meetings and to find the next meeting
# that includes a given attendee.


###################################################################################################
# Manager class                                                                                   #
###################################################################################################


class CalendarManager:

    def __init__(self, calendarAccessor):
        """constructor, initialize the object"""
        self.calendar = calendarAccessor

    def createMeeting(self, description, startTime, attendeeNames):
        meetingId = self.calendar.createMeeting(description, startTime, attendeeNames)
        return meetingId
 #was originally named find next meeting
    def findEarliestMeetingIncludingAttendee(self, name):
        meetingInfo = self.calendar.findEarliestMeetingIncludingAttendee(name)
        return meetingInfo  # return meeting information

###################################################################################################
# In-Memory Accessor class                                                                        #
###################################################################################################


class InMemoryCalendarAccessor:

    def __init__(self):
        self.calendar = InMemoryCalendar()

    def createMeeting(self, description, startTime, attendeeNames):
        meeting = self.calendar.createMeeting(description, startTime, attendeeNames)
        return meeting.getId()

    #renaming to imporve clarity
    def findEarliestMeetingIncludingAttendee(self, name):
        meeting = self.calendar.findEarliestMeetingIncludingAttendee(name)
        # return meeting
        return self._getMeetingInfo(meeting) if meeting is not None else None

    def _getMeetingInfo(self, meeting):
        mInfo = MeetingInfo(meeting.getId(), meeting.getDescription(), meeting.getStartTime())
        return mInfo

###################################################################################################
# dataclass                                                                                       #
###################################################################################################


@dataclass
class MeetingInfo:
    id: int
    description: str
    startTime: datetime

    def __repr__(self):
        return f"Meeting {self.id} \"{self.description}\" at {self.startTime}"

###################################################################################################
# Calendar class                                                                                  #
###################################################################################################


class InMemoryCalendar:

    def __init__(self):
        self.meetings = []

    def createMeeting(self, description, startTime, attendeeNames):
        meeting = Meeting(description, startTime, attendeeNames)
        self.addMeeting(meeting)
        return meeting

    def addMeeting(self, meeting):
        self.meetings.append(meeting)
        self.meetings.sort(key=lambda meeting: meeting.getStartTime())

    def findEarliestMeetingIncludingAttendee(self, name):
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

    def __init__(self, description, startTime, attendeeNames):
        if not attendeeNames:
            raise ValueError("Meeting must have one or more attendees")
        self.id = self.idGenerator.next()
        self.description = description
        self.attendees = [self._createAttendee(name) for name in attendeeNames]
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
        attendeeNames = ",".join(map(str, self.attendees))
        return f"Meeting {self.id} description: {self.description} starting: {self.startTime} attendees: {attendeeNames}"

###################################################################################################
# Contact class                                                                                   #
###################################################################################################


class Contact:

    def __init__(self, name):
        self.name = name

    def getName(self):
        return self.name

    def __repr__(self):
        return self.name

###################################################################################################
# Contact Tests                                                                                   #
###################################################################################################


# fixtures
@pytest.fixture
def manager():
    accessor = InMemoryCalendarAccessor()
    return CalendarManager(accessor)


@pytest.fixture
def scenario1_meetings_manager(manager):
    manager.createMeeting("First Meeting", datetime(2021,5,17,9,10), ["Wolfgang"])
    manager.createMeeting("Second Meeting", datetime(2021,5,17,11,10), ["Wolfgang","Mei","Matt"])
    manager.createMeeting("Third Meeting", datetime(2021,5,17,14,10), ["Matt"])
    return manager


# test if find meeting works
def test_find_next_meeting(scenario1_meetings_manager):
    # run some code
    meeting = scenario1_meetings_manager.findEarliestMeetingIncludingAttendee("Matt")
    # check that the correct meeting is returned
    assert meeting.description == "Second Meeting"


# test if creating meetings works
def test_meeting2(manager):
    with pytest.raises(ValueError):
        manager.createMeeting("Meeting nobody attends", datetime(2021,5,17,1,0), [])


# another fixture
@pytest.fixture
def scenario2_meetings_manager(manager):
    """create some meetings"""
    manager.createMeeting("Morning Meeting", datetime(2021,5,24,9,10), ["Alice"])
    manager.createMeeting("Afternoon Meeting", datetime(2021,5,24,15,0), ["Bob","Charlie"])
    manager.createMeeting("Lunch Meeting", datetime(2021,5,24,12,0), ["Alice","Bob","Charlie"])
    return manager


# test if find meeting works for the lunch meeting
def test_find_next_meeting_reordered(scenario2_meetings_manager):
    meeting = scenario2_meetings_manager.findEarliestMeetingIncludingAttendee("Bob")
    assert meeting.description == "Lunch Meeting"


# test if the manager works
def test_mgr_findEarliestMeetingIncludingAttendee_calls_accessor():
    accessor = Mock()
    manager = CalendarManager(accessor)
    manager.findEarliestMeetingIncludingAttendee("Alice")
    assert accessor.findEarliestMeetingIncludingAttendee.called_once_with("Alice")


# test if the manager works
def test_mgr_findEarliestMeetingIncludingAttendee_result():
    expected = MeetingInfo("Nonexistant meeting", datetime(2021,5,24,7,0),["Alice"])
    accessor = Mock()
    accessor.findEarliestMeetingIncludingAttendee.return_value = expected
    manager = CalendarManager(accessor)
    meeting = manager.findEarliestMeetingIncludingAttendee  ("Alice")
    assert meeting == expected


###################################################################################################
# main functions                                                                                  #
###################################################################################################
def createDummyMeetings(manager):
    manager.createMeeting("First Meeting", datetime(2021,5,17,9,10), ["Wolfgang"])
    manager.createMeeting("Second Meeting", datetime(2021,5,17,11,10), ["Wolfgang","Mei","Matt"])
    manager.createMeeting("Third Meeting", datetime(2021,5,17,14,10), ["Matt"])


def checkFindMeeting(manager):
    nextMeetingInfo = manager.findEarliestMeetingIncludingAttendee("Matt")
    print("The next meeting with Matt is:")
    print(nextMeetingInfo)


def main():
    accessor = InMemoryCalendarAccessor()
    manager = CalendarManager(accessor)
    createDummyMeetings(manager)
    checkFindMeeting(manager)


# run main if necessary
if __name__ == "__main__":
    main()
