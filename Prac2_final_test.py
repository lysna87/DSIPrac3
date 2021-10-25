from datetime import datetime
from unittest.mock import Mock
import pytest
from Prac2_final_code import CalendarManager, InMemoryCalendarAccessor, MeetingInfo

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
    meeting = scenario1_meetings_manager.findNextMeeting("Matt")
    assert meeting.description == "Second Meeting"

def test_meeting_must_have_attendees(manager):
    with pytest.raises(ValueError):
        manager.createMeeting("Meeting nobody attends", datetime(2021,5,17,1,0), [])

@pytest.fixture #lunch meeting fails until I manually changed lunch and afternoon.
def scenario2_meetings_manager(manager):
    manager.createMeeting("Morning Meeting", datetime(2021,5,24,9,10), ["Alice"])
    manager.createMeeting("Lunch Meeting", datetime(2021,5,24,15,0), ["Bob","Charlie"])
    manager.createMeeting("Afternoon Meeting", datetime(2021,5,24,12,0), ["Alice","Bob","Charlie"])
    return manager

def test_find_next_meeting_reordered(scenario2_meetings_manager):
    meeting = scenario2_meetings_manager.findNextMeeting("Bob")
    assert meeting.description == "Lunch Meeting"

def test_mgr_findNextMeeting_calls_accessor():
    accessor = Mock()
    manager = CalendarManager(accessor)
    manager.findNextMeeting("Alice")
    assert accessor.findNextMeeting.called_once_with("Alice")

def test_mgr_findNextMeeting_result():
    expected = MeetingInfo("Nonexistant meeting", datetime(2021,5,24,7,0),["Alice"])
    accessor = Mock()
    accessor.findNextMeeting.return_value = expected
    manager = CalendarManager(accessor)
    meeting = manager.findNextMeeting("Alice")
    assert meeting == expected