import unittest
from unittest.mock import patch
from hr_time.api.worklog.api import has_employee_made_worklogs_today, create_worklog

from hr_time.api.worklog.repository import Worklog, WorklogRepository
from hr_time.api.worklog.service import WorklogService


class TestWorklogAPI(unittest.TestCase):
    worklog: WorklogRepository
    service: WorklogService

    def setUp(self):
        super().setUp()
        self.worklog = WorklogRepository()
        self.service = WorklogService(self.worklog)

        # Patch the get_worklogs_of_employee_on_date method multiple tests in this class
        patcher_worklogs = patch(
            'hr_time.api.flextime.processing.WorklogRepository.get_worklogs_of_employee_on_date')

        # Start the patch
        self.mock_get_worklogs_of_employee_on_date = patcher_worklogs.start()
        # Mock return value for WorklogRepository.get_worklogs_of_employee_on_date
        self.mock_get_worklogs_of_employee_on_date.return_value = [
            Worklog("001", "2023-11-19 08:00:00", "Task A", "T001"),
            Worklog("001", "2023-11-19 09:00:00", "Task B", "T002")
        ]

        # Add cleanup to stop patching after the test
        self.addCleanup(patcher_worklogs.stop)

    @patch('hr_time.api.worklog.service.WorklogService')
    def test_has_employee_made_worklogs_today_positive(self, MockWorklogService):
        # Arrange
        employee_id = '001'
        # Create a mock instance of WorklogService
        mock_service_instance = MockWorklogService.return_value
        # Mock the return value
        mock_service_instance.check_if_employee_has_worklogs_today.return_value = True

        # Act
        result = has_employee_made_worklogs_today(
            employee_id)  # Call the API method

        # Assert
        self.assertTrue(result)  # Assert that the result is True
        mock_service_instance.check_if_employee_has_worklogs_today.assert_called_once_with(
            employee_id)  # Verify the call

    @patch('hr_time.api.worklog.service.WorklogService')
    def test_has_employee_made_worklogs_today_negative(self, MockWorklogService):
        # Arrange
        employee_id = '001'
        # Create a mock instance of WorklogService
        mock_service_instance = MockWorklogService.return_value
        # Mock the return value
        mock_service_instance.check_if_employee_has_worklogs_today.return_value = False

        # Act
        result = has_employee_made_worklogs_today(
            employee_id)  # Call the API method

        # Assert
        self.assertFalse(result)  # Assert that the result is False
        mock_service_instance.check_if_employee_has_worklogs_today.assert_called_once_with(
            employee_id)  # Verify the call

    @patch('hr_time.api.worklog.service.WorklogService')
    def test_create_worklog_success(self, MockWorklogService):
        # Arrange
        employee_id = '001'
        worklog_text = 'Completed task A'
        task = 'TASK001'
        # Create a mock instance of WorklogService
        mock_service_instance = MockWorklogService.return_value
        mock_service_instance.create_worklog.return_value = {
            'status': 'success', 'message': 'Worklog created successfully'}  # Mock the return value

        # Act
        result = create_worklog(employee_id, worklog_text,
                                task)  # Call the API method

        # Assert
        self.assertEqual(result['status'], 'success')  # Assert the status
        # Assert the message
        self.assertEqual(result['message'], 'Worklog created successfully')
        mock_service_instance.create_worklog.assert_called_once_with(
            employee_id, worklog_text, task)  # Verify the call

    def test_create_worklog_empty_description(self):
        # Arrange
        employee_id = '001'
        worklog_text = ''  # Empty worklog description
        task = 'TASK001'

        # Act
        result = create_worklog(employee_id, worklog_text,
                                task)  # Call the API method

        # Assert
        self.assertEqual(result['status'], 'error')  # Expect an error status
        # Expect the error message
        self.assertEqual(result['message'],
                         "Worklog description cannot be empty")

    @patch('hr_time.api.worklog.repository.WorklogRepository.create_worklog')
    def test_create_worklog_general_exception(self, mock_create_worklog):
        # Arrange
        employee_id = '001'
        worklog_text = 'Completed task B'
        task = 'TASK002'
        mock_create_worklog.side_effect = Exception(
            "Database connection failed")  # Simulate a general exception

        # Act
        result = create_worklog(employee_id, worklog_text,
                                task)  # Call the API method

        # Assert
        self.assertEqual(result['status'], 'error')  # Expect an error status
        # Expect the error message
        self.assertEqual(result['message'], "Database connection failed")
