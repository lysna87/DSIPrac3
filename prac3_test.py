from datetime import datetime
from unittest.mock import Mock
from Prac3_final_codeHL import CalendarManager, InMemoryCalendarAccessor
import pytest
#Notes for Heather: When changing tests, save before rerunning them

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

def test_find_next_meeting(scenario1_meetings_manager):
    meeting = scenario1_meetings_manager.findEarliestMeetingIncludingAttendee("Matt")
    assert meeting.description == "Second Meeting"
