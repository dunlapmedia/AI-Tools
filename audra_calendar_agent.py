from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import caldav
import json
import pytz
from requests import post

class AuDRACalendarAgent:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/calendar']
        self.CATEGORIES = [
            'Work', 'Free', 'Breakfast', 'Brunch', 'Lunch', 'Afternoon Tea', 'Dinner', 
            'Workout', 'Laundry and Cleaning', 'Sleep', 'Writing', 'Bri', 'Health', 'SSS',
            'Travel'  # Added Travel category
        ]
        self.google_service = None
        self.apple_client = None
        self.testcal = None
        self.CATEGORY_MINIMUMS = [
            {
                'category': 'Work',
                'daily': 7,     # 7 hours per day
                'weekly': 28,   # 28 hours per week
                'monthly': 0    # No monthly minimum
            },
            {
                'category': 'Sleep',
                'daily': 6.5,   # 6.5 hours per day
                'weekly': 49,   # 49 hours per week
                'monthly': 210  # ~210 hours per month
            },
            {
                'category': 'Workout',
                'daily': 0,   # 1.5 hours per day
                'weekly': 5,  # 7.5 hours per week
                'monthly': 20   # 28 hours per month
            },
            {
                'category': 'Free',
                'daily': 2,     # 2 hours per day
                'weekly': 14,   # 14 hours per week
                'monthly': 56   # ~56 hours per month
            },
            {
                'category': 'Breakfast',
                'daily': 0.5,   # 30 minutes per day
                'weekly': 3.5,  # 3.5 hours per week
                'monthly': 15   # 15 hours per month
            },
            {
                'category': 'Brunch',
                'daily': 0,     # Not required daily
                'weekly': 0,    # No weekly minimum
                'monthly': 3    # 3 hours per month
            },
            {
                'category': 'Lunch',
                'daily': 1,     # 1 hour per day
                'weekly': 5,    # 5 hours per week
                'monthly': 20   # 20 hours per month
            },
            {
                'category': 'Afternoon Tea',
                'daily': 0,     # Not required daily
                'weekly': 1.5,  # 1.5 hours per week
                'monthly': 6    # 6 hours per month
            },
            {
                'category': 'Dinner',
                'daily': 1.5,     # 1 hour per day
                'weekly': 8,    # 7 hours per week
                'monthly': 30   # 30 hours per month
            },
            {
                'category': 'Laundry and Cleaning',
                'daily': 0,     # Not required daily
                'weekly': 3,    # 3 hours per week
                'monthly': 12   # 12 hours per month
            },
            {
                'category': 'Writing',
                'daily': 1.5,     # 2 hours per day
                'weekly': 8,   # 10 hours per week
                'monthly': 30   # 40 hours per month
            },
            {
                'category': 'Bri',
                'daily': 1,     # 1 hour per day
                'weekly': 7,   # 10 hours per week
                'monthly': 28   # 40 hours per month
            },
            {
                'category': 'Health',
                'daily': 0,     # Not required daily
                'weekly': 0,    # No weekly minimum
                'monthly': 0    # No monthly minimum
            },
            {
                'category': 'SSS',
                'daily': 1,     # 1 hour per day
                'weekly': 7,    # 7 hours per week
                'monthly': 28   # 28 hours per month
            },
            {
                'category': 'Travel',
                'daily': 0,     # No daily minimum
                'weekly': 0,    # No weekly minimum
                'monthly': 0    # No monthly minimum
            }
        ]
        self.CATEGORY_CONSTRAINTS = {
            'Sleep': {
                'preferred_start_time': '22:00',  # 10 PM
                'preferred_end_time': '08:30',    # 8:30 AM
                'consecutive_hours': True,         # Hours should be consecutive
                'weekday_only': False,            # Applies all days
            },
            'Work': {
                'preferred_start_time': '09:00',  # 9 AM
                'preferred_end_time': '17:00',    # 5 PM
                'consecutive_hours': True,         # Hours should be consecutive
                'weekday_only': True,             # Monday-Friday only
            },
            'Workout': {
                'preferred_start_time': '06:00',  # 6 AM
                'preferred_end_time': '20:00',    # 8 PM
                'consecutive_hours': False,         # Hours should be consecutive
                'weekday_only': False,            # Applies all days
            },
            'Free': {
                'preferred_start_time': '09:00',  # 5 PM
                'preferred_end_time': '22:00',    # 10 PM
                'consecutive_hours': False,        # Can be split
                'weekday_only': False,            # Applies all days
            },
            'Breakfast': {
                'preferred_start_time': '07:00',  # 7 AM
                'preferred_end_time': '09:00',    # 9 AM
                'consecutive_hours': True,         # Should be consecutive
                'weekday_only': False,            # Applies all days
            },
            'Brunch': {
                'preferred_start_time': '10:00',  # 10 AM
                'preferred_end_time': '12:00',    # 12 PM
                'consecutive_hours': True,         # Should be consecutive
                'weekday_only': False,            # Applies all days
            },
            'Lunch': {
                'preferred_start_time': '12:00',  # 12 PM
                'preferred_end_time': '14:00',    # 2 PM
                'consecutive_hours': True,         # Should be consecutive
                'weekday_only': False,            # Applies all days
            },
            'Afternoon Tea': {
                'preferred_start_time': '15:00',  # 3 PM
                'preferred_end_time': '16:00',    # 4 PM
                'consecutive_hours': True,         # Should be consecutive
                'weekday_only': False,            # Applies all days
            },
            'Dinner': {
                'preferred_start_time': '17:30',  # 5:30 PM
                'preferred_end_time': '20:00',    # 8 PM
                'consecutive_hours': True,         # Should be consecutive
                'weekday_only': False,            # Applies all days
            },
            'Laundry and Cleaning': {
                'preferred_start_time': '09:00',  # 9 AM
                'preferred_end_time': '20:00',    # 8 PM
                'consecutive_hours': False,        # Can be split
                'weekday_only': False,            # Applies all days
            },
            'Writing': {
                'preferred_start_time': '09:00',  # 9 AM
                'preferred_end_time': '23:59',    # 11:59 PM
                'consecutive_hours': True,         # Should be consecutive
                'weekday_only': False,             # Weekdays preferred
            },
            'Bri': {
                'preferred_start_time': '10:00',  # 10 AM
                'preferred_end_time': '22:00',    # 10 PM
                'consecutive_hours': True,         # Should be consecutive
                'weekday_only': False,            # Applies all days
            },
            'Health': {
                'preferred_start_time': '08:00',  # 8 AM
                'preferred_end_time': '17:00',    # 5 PM
                'consecutive_hours': True,         # Should be consecutive
                'weekday_only': True,             # Most medical appointments are weekdays
            },
            'SSS': {
                'preferred_start_time': '06:00',  # 6 AM
                'preferred_end_time': '09:00',    # 9 AM
                'consecutive_hours': True,         # Should be consecutive
                'weekday_only': False,            # Applies all days
            },
            'Travel': {
                'preferred_start_time': '00:00',  # Any time
                'preferred_end_time': '23:59',    # Any time
                'consecutive_hours': True,         # Should be consecutive
                'weekday_only': False,            # Applies all days
            }
        }
        self.ollama_url = "http://localhost:7869/api/generate"
        self.ai_model = "llama3.2"  # Default model

    def authenticate_google(self, credentials_path):
        """Authenticate with Google Calendar API"""
        flow = InstalledAppFlow.from_client_secrets_file(
            credentials_path, self.SCOPES)
        creds = flow.run_local_server(port=0)
        self.google_service = build('calendar', 'v3', credentials=creds)

    def authenticate_apple(self, caldav_url, username, password):
        """Authenticate with Apple Calendar via CalDAV"""
        self.apple_client = caldav.DAVClient(
            url=caldav_url,
            username=username,
            password=password
        )

def query_ollama(self, prompt):
    """
    Query Ollama AI model for decision making
    """
    try:
        response = post(self.ollama_url, json={
            "model": self.ai_model,
            "prompt": prompt,
            "stream": False
        })
        if response.status_code == 200:
            return response.json()['response']
        return None
    except Exception as e:
        print(f"Error querying Ollama: {e}")
        return None

    def get_next_month_range(self):
        """Get the date range for next month"""
        today = datetime.now()
        first_of_next_month = datetime(today.year + ((today.month) // 12),
                                     ((today.month % 12) + 1),
                                     1)
        last_of_next_month = (first_of_next_month.replace(day=28) + 
                             timedelta(days=4)).replace(day=1) - timedelta(days=1)
        return first_of_next_month, last_of_next_month

    def read_google_calendars(self):
        """Read events from Google calendars (Personal and Family)"""
        if not self.google_service:
            raise Exception("Google Calendar not authenticated")

        start_date, end_date = self.get_next_month_range()
        events = []

        for calendar_name in ['Personal', 'Family']:
            calendar_list = self.google_service.calendarList().list().execute()
            calendar_id = None
            
            for calendar in calendar_list['items']:
                if calendar['summary'] == calendar_name:
                    calendar_id = calendar['id']
                    break

            if calendar_id:
                events_result = self.google_service.events().list(
                    calendarId=calendar_id,
                    timeMin=start_date.isoformat() + 'Z',
                    timeMax=end_date.isoformat() + 'Z',
                    singleEvents=True,
                    orderBy='startTime'
                ).execute()
                events.extend(events_result.get('items', []))

        return events

    def read_apple_calendars(self):
        """Read events from Apple calendars (Personal and Family)"""
        if not self.apple_client:
            raise Exception("Apple Calendar not authenticated")

        start_date, end_date = self.get_next_month_range()
        events = []

        for calendar_name in ['Personal', 'Family']:
            principal = self.apple_client.principal()
            calendars = principal.calendars()
            
            for calendar in calendars:
                if calendar.name == calendar_name:
                    cal_events = calendar.date_search(
                        start=start_date,
                        end=end_date
                    )
                    events.extend(cal_events)

        return events

    def categorize_event(self, event):
        """Determine category for an event based on title and description"""
        title = event.get('summary', '').lower()
        description = event.get('description', '').lower()
        location = event.get('location', '').lower()
        
        # Check for virtual work meetings
        if ('virtual' in location or 'zoom' in location or 'teams' in location or 
            'meet.google.com' in location):
            if any(word in title or word in description for word in 
                  ['meeting', 'conference', 'presentation', 'call']):
                return 'Work'
        
        # Bri (highest priority)
        if any(word in title or word in description for word in 
               ['bri', 'date', 'anniversary', 'couple']):
            return 'Bri'
        
        # Work (second priority)
        if any(word in title or word in description for word in 
               ['work', 'meeting', 'project', 'conference', 'presentation', 
                'deadline', 'interview', 'client', 'report', 'office']):
            return 'Work'
        
        # Writing (third priority)
        if any(word in title or word in description for word in 
               ['writing', 'blog', 'article', 'draft', 'edit', 'compose', 
                'document', 'manuscript']):
            return 'Writing'
        
        # Workout (fourth priority)
        if any(word in title or word in description for word in 
               ['workout', 'gym', 'exercise', 'training', 'run', 'fitness', 
                'yoga', 'swimming', 'sports']):
            return 'Workout'
        
        # Meal categories
        if any(word in title or word in description for word in 
               ['breakfast', 'morning meal', 'second breakfast']):
            return 'Breakfast'
        if any(word in title or word in description for word in
               ['elevenses', 'brunch', 'mid-morning meal']):
            return 'Brunch'
        if any(word in title or word in description for word in 
                ['lunch', 'luncheon', 'noon meal']):
            return 'Lunch'
        if any(word in title or word in description for word in 
                ['afternoon snack', 'tea', 'light meal']):
            return 'Afternoon Tea'
        if any(word in title or word in description for word in 
                ['dinner', 'supper', 'evening meal']):
            return 'Dinner'
        
        # Laundry and Cleaning
        if any(word in title or word in description for word in 
               ['laundry', 'cleaning', 'chores', 'housework', 'vacuum', 
                'dishes', 'tidying', 'organize']):
            return 'Laundry and Cleaning'
        
        # Sleep
        if any(word in title or word in description for word in 
               ['sleep', 'nap', 'rest', 'bedtime']):
            return 'Sleep'
        
        # Health category
        if any(word in title or word in description for word in 
               ['doctor', 'medical', 'appointment', 'checkup', 'dentist',
                'therapy', 'medication', 'hospital', 'clinic', 'physician',
                'health', 'wellness', 'prescription', 'mental health',
                'counseling', 'consultation', 'optometrist', 'specialist',
                'physical therapy', 'vaccination', 'blood work']):
            return 'Health'
        
        # Travel category (add before Free time check)
        if any(word in title or word in description for word in 
               ['travel', 'flight', 'train', 'bus', 'drive', 'trip', 'journey',
                'airport', 'station', 'departure', 'arrival', 'transit',
                'commute', 'layover', 'connecting', 'vacation', 'hotel',
                'booking', 'rental car', 'uber', 'lyft', 'taxi']):
            return 'Travel'
        
        # Free time (including gaming and streaming activities)
        if any(word in title or word in description for word in 
               ['free', 'break', 'relax', 'leisure', 'personal time',
                'video games', 'gaming', 'ps5', 'playstation', 'xbox', 
                'nintendo', 'switch', 'civ', 'civilization', 'twitch',
                'stream', 'streaming', 'd&d', 'dnd', 'dungeons and dragons',
                'game night', 'rpg', 'mmo', 'multiplayer', 'discord',
                'minecraft', 'fortnite', 'warzone', 'apex']):
            return 'Free'
        
        return 'Free'  # Default category if no matches found

    def add_to_testcal(self, event, category):
        """Add event to testcal with category"""
        if not self.google_service:
            raise Exception("Google Calendar not authenticated")

        # Find or create testcal
        calendar_list = self.google_service.calendarList().list().execute()
        testcal_id = None
        
        for calendar in calendar_list['items']:
            if calendar['summary'] == 'testcal':
                testcal_id = calendar['id']
                break

        if not testcal_id:
            # Create testcal if it doesn't exist
            calendar = {
                'summary': 'testcal',
                'timeZone': 'UTC'
            }
            created_calendar = self.google_service.calendars().insert(
                body=calendar).execute()
            testcal_id = created_calendar['id']

        # Prepare event with category
        event['description'] = f"{event.get('description', '')}\n[Category:{category}]"
        
        # Add event to testcal
        self.google_service.events().insert(
            calendarId=testcal_id,
            body=event
        ).execute()

    def remove_category_events(self, category):
        """Remove all events with specified category from testcal"""
        if not self.google_service:
            raise Exception("Google Calendar not authenticated")

        # Find testcal
        calendar_list = self.google_service.calendarList().list().execute()
        testcal_id = None
        
        for calendar in calendar_list['items']:
            if calendar['summary'] == 'testcal':
                testcal_id = calendar['id']
                break

        if testcal_id:
            events_result = self.google_service.events().list(
                calendarId=testcal_id,
                singleEvents=True
            ).execute()

            for event in events_result.get('items', []):
                if f"[Category:{category}]" in event.get('description', ''):
                    self.google_service.events().delete(
                        calendarId=testcal_id,
                        eventId=event['id']
                    ).execute()

    def adjust_event_time(self, event_id, new_start_time, new_end_time):
        """Adjust start and end time for an event in testcal"""
        if not self.google_service:
            raise Exception("Google Calendar not authenticated")

        calendar_list = self.google_service.calendarList().list().execute()
        testcal_id = None
        
        for calendar in calendar_list['items']:
            if calendar['summary'] == 'testcal':
                testcal_id = calendar['id']
                break

        if testcal_id:
            event = self.google_service.events().get(
                calendarId=testcal_id,
                eventId=event_id
            ).execute()

            event['start']['dateTime'] = new_start_time.isoformat()
            event['end']['dateTime'] = new_end_time.isoformat()

            self.google_service.events().update(
                calendarId=testcal_id,
                eventId=event_id,
                body=event
            ).execute()

    def get_availability(self, start_date, end_date):
        """Retrieve availability from testcal"""
        if not self.google_service:
            raise Exception("Google Calendar not authenticated")

        calendar_list = self.google_service.calendarList().list().execute()
        testcal_id = None
        
        for calendar in calendar_list['items']:
            if calendar['summary'] == 'testcal':
                testcal_id = calendar['id']
                break

        if testcal_id:
            free_busy_query = {
                'timeMin': start_date.isoformat(),
                'timeMax': end_date.isoformat(),
                'items': [{'id': testcal_id}]
            }

            free_busy = self.google_service.freebusy().query(
                body=free_busy_query
            ).execute()

            return free_busy.get('calendars', {}).get(testcal_id, {}).get('busy', [])

    def create_new_event(self, title, start_time, end_time, description="", category=None):
        """Create and add a new event to testcal"""
        if not self.google_service:
            raise Exception("Google Calendar not authenticated")

        # Get testcal ID
        calendar_list = self.google_service.calendarList().list().execute()
        testcal_id = next((cal['id'] for cal in calendar_list['items'] 
                          if cal['summary'] == 'testcal'), None)

        if testcal_id:
            # Check if this is a work event and determine location
            location = None
            if category == 'Work':
                # Check if it's Tuesday (1), Wednesday (2), or Thursday (3)
                if start_time.weekday() in [1, 2, 3]:
                    # Check for non-virtual, non-work events before 3 PM
                    day_start = start_time.replace(hour=0, minute=0, second=0)
                    cutoff_time = start_time.replace(hour=15, minute=0, second=0)
                    
                    events_result = self.google_service.events().list(
                        calendarId=testcal_id,
                        timeMin=day_start.isoformat() + 'Z',
                        timeMax=cutoff_time.isoformat() + 'Z',
                        singleEvents=True
                    ).execute()

                    has_in_person_event = False
                    for event in events_result.get('items', []):
                        event_category = next((cat for cat in self.CATEGORIES 
                                            if f"[Category:{cat}]" in event.get('description', '')), None)
                        if (event_category != 'Work' and 
                            event.get('location') and 
                            'virtual' not in event.get('location', '').lower()):
                            has_in_person_event = True
                            break

                    if not has_in_person_event:
                        location = "141 W Jackson Blvd, Chicago, IL"

            event = {
                'summary': title,
                'description': f"{description}\n[Category:{category}]" if category else description,
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'UTC',
                },
            }

            # Add location if set
            if location:
                event['location'] = location

            return self.google_service.events().insert(
                calendarId=testcal_id,
                body=event
            ).execute()

    def calculate_category_hours(self, start_date=None, end_date=None):
        """
        Calculate total hours spent on each category within a date range
        Args:
            start_date (datetime): Start date for calculation (inclusive)
            end_date (datetime): End date for calculation (inclusive)
        Returns:
            tuple: (success boolean, dictionary of category hours)
        """
        if not self.google_service:
            raise Exception("Google Calendar not authenticated")

        # If no dates provided, use next month range
        if start_date is None or end_date is None:
            start_date, end_date = self.get_next_month_range()
        
        # Ensure end_date includes the full day
        end_date = end_date.replace(hour=23, minute=59, minute=59)

        calendar_list = self.google_service.calendarList().list().execute()
        testcal_id = None
        
        for calendar in calendar_list['items']:
            if calendar['summary'] == 'testcal':
                testcal_id = calendar['id']
                break

        if testcal_id:
            events_result = self.google_service.events().list(
                calendarId=testcal_id,
                timeMin=start_date.isoformat() + 'Z',
                timeMax=end_date.isoformat() + 'Z',
                singleEvents=True
            ).execute()

            category_hours = {category: 0 for category in self.CATEGORIES}

            for event in events_result.get('items', []):
                description = event.get('description', '')
                for category in self.CATEGORIES:
                    if f"[Category:{category}]" in description:
                        # Parse event start and end times
                        start = datetime.fromisoformat(
                            event['start'].get('dateTime', event['start'].get('date')))
                        end = datetime.fromisoformat(
                            event['end'].get('dateTime', event['end'].get('date')))
                        
                        # Adjust start time if before requested start_date
                        if start < start_date:
                            start = start_date
                        # Adjust end time if after requested end_date
                        if end > end_date:
                            end = end_date
                        
                        duration = (end - start).total_seconds() / 3600
                        category_hours[category] += duration

            return True, category_hours

        return False, {}

    def fill_minimum_hours(self, start_date, end_date):
        """
        Fill calendar with events to meet minimum category hours using AI assistance
        """
        if not self.google_service:
            raise Exception("Google Calendar not authenticated")

        # Get current availability
        busy_slots = self.get_availability(start_date, end_date)
        success, current_hours = self.calculate_category_hours(start_date, end_date)
        if not success:
            return False

        total_days = (end_date - start_date).days + 1
        total_weeks = total_days // 7

        # Create available time slots
        available_slots = []
        current_time = start_date
        
        # Convert busy slots to datetime objects
        busy_periods = [(datetime.fromisoformat(slot['start'].replace('Z', '')),
                        datetime.fromisoformat(slot['end'].replace('Z', '')))
                       for slot in busy_slots]

        # Find available slots
        while current_time < end_date:
            slot_start = current_time
            
            # Find next busy period or end of day
            next_busy = None
            for busy_start, busy_end in busy_periods:
                if busy_start > current_time:
                    if next_busy is None or busy_start < next_busy:
                        next_busy = busy_start
            
            slot_end = (next_busy if next_busy 
                       else current_time.replace(hour=23, minute=59, second=59))
            
            # Only add slots longer than 30 minutes
            if (slot_end - slot_start).total_seconds() > 1800:  # 30 minutes
                available_slots.append((slot_start, slot_end))
            
            current_time = (next_busy if next_busy 
                          else (current_time + timedelta(days=1)).replace(
                              hour=0, minute=0, second=0))

        # Process Sleep first to establish base schedule
        sleep_category = next((cat for cat in self.CATEGORY_MINIMUMS 
                             if cat['category'] == 'Sleep'), None)
        workout_category = next((cat for cat in self.CATEGORY_MINIMUMS 
                               if cat['category'] == 'Workout'), None)
        sss_category = next((cat for cat in self.CATEGORY_MINIMUMS 
                           if cat['category'] == 'SSS'), None)
        
        # Remove these categories from regular processing
        remaining_categories = [cat for cat in self.CATEGORY_MINIMUMS 
                              if cat['category'] not in ['Sleep', 'Workout', 'SSS']]

        # Process Sleep slots first
        if sleep_category:
            # Calculate needed hours for Sleep
            daily_sleep_need = sleep_category['daily'] * total_days
            weekly_sleep_need = sleep_category['weekly'] * total_weeks
            monthly_sleep_need = sleep_category['monthly']
            sleep_needed_hours = max(daily_sleep_need, weekly_sleep_need, monthly_sleep_need) - current_hours.get('Sleep', 0)

            # Apply sleep maximum of 8 hours per day
            max_sleep_hours = 8 * total_days
            if sleep_needed_hours > max_sleep_hours - current_hours.get('Sleep', 0):
                sleep_needed_hours = max(0, max_sleep_hours - current_hours.get('Sleep', 0))

            if sleep_needed_hours > 0:
                # Ask AI for optimal sleep schedule
                sleep_prompt = f"""
                Help schedule {sleep_needed_hours} hours of Sleep with these constraints:
                - Preferred start time: {sleep_category.get('preferred_start_time', 'any')}
                - Preferred end time: {sleep_category.get('preferred_end_time', 'any')}
                - Must be consecutive hours: {sleep_category.get('consecutive_hours', False)}
                - Weekday only: {sleep_category.get('weekday_only', False)}
                - Current available slots: {len(available_slots)} slots
                
                Should we: 
                1. Schedule in larger blocks
                2. Split into smaller sessions
                3. Stick strictly to preferred times
                4. Be flexible with timing
                
                Respond with ONLY the number of your recommendation (1-4).
                """
                
                sleep_strategy = self.query_ollama(sleep_prompt)
                try:
                    sleep_strategy = int(sleep_strategy.strip())
                except:
                    sleep_strategy = 1  # Default to larger blocks if AI fails
                    
                hours_to_fill = sleep_needed_hours
                available_slots = sorted(available_slots, key=lambda x: x[0])
                
                for start, end in available_slots:
                    if hours_to_fill <= 0:
                        break
                        
                    # Check constraints
                    if sleep_category.get('weekday_only') and start.weekday() >= 5:
                        continue
                        
                    slot_start_time = start.strftime('%H:%M')
                    if (sleep_category.get('preferred_start_time') and 
                        slot_start_time < sleep_category['preferred_start_time']):
                        continue
                        
                    if (sleep_category.get('preferred_end_time') and 
                        end.strftime('%H:%M') > sleep_category['preferred_end_time']):
                        continue
                    
                    slot_duration = (end - start).total_seconds() / 3600
                    
                    # Apply AI strategy
                    if sleep_strategy == 1:  # Larger blocks
                        min_duration = 2.0  # Minimum 2 hours
                    elif sleep_strategy == 2:  # Smaller sessions
                        min_duration = 0.5  # 30 minutes
                    else:  # Strategy 3 or 4
                        min_duration = 1.0  # 1 hour
                    
                    if slot_duration >= min_duration:
                        hours_to_use = min(
                            slot_duration,
                            hours_to_fill if sleep_strategy != 2 else min(2.0, hours_to_fill)
                        )
                        
                        event_end = start + timedelta(hours=hours_to_use)
                        
                        # Create the event
                        self.create_new_event(
                            title="Scheduled Sleep",
                            start_time=start,
                            end_time=event_end,
                            description=(f"Automatically scheduled to meet minimum hours\n"
                                       f"AI Strategy: {sleep_strategy}"),
                            category="Sleep"
                        )
                        
                        hours_to_fill -= hours_to_use
                        
                        # Update available slot
                        if hours_to_use < slot_duration:
                            available_slots.append((event_end, end))
                
                available_slots.sort(key=lambda x: x[0])

            # After each Sleep slot, schedule SSS and potentially Workout
            for start, end in available_slots[:]:
                if '[Category:Sleep]' in self.get_events_at_time(start):
                    sleep_end = end
                    
                    # Schedule SSS immediately after Sleep
                    sss_duration = 1  # 1 hour for SSS
                    sss_end = sleep_end + timedelta(hours=sss_duration)
                    
                    # Check if it's morning hours (before 9 AM)
                    is_morning = sleep_end.hour < 9
                    
                    if is_morning and workout_category:
                        # Schedule Workout between Sleep and SSS
                        workout_duration = 1.5  # 1.5 hours for morning workout
                        self.create_new_event(
                            title="Scheduled Workout",
                            start_time=sleep_end,
                            end_time=sleep_end + timedelta(hours=workout_duration),
                            description="Morning workout following sleep",
                            category="Workout"
                        )
                        
                        # Adjust SSS start time to follow workout
                        sss_start = sleep_end + timedelta(hours=workout_duration)
                        self.create_new_event(
                            title="Scheduled SSS",
                            start_time=sss_start,
                            end_time=sss_start + timedelta(hours=sss_duration),
                            description="Morning SSS following workout",
                            category="SSS"
                        )
                    else:
                        # Just schedule SSS after Sleep
                        self.create_new_event(
                            title="Scheduled SSS",
                            start_time=sleep_end,
                            end_time=sss_end,
                            description="SSS following sleep",
                            category="SSS"
                        )
                    
                    # Update available slots
                    self.update_available_slots(available_slots)

        # Process remaining categories
        for category_min in remaining_categories:
            category = category_min['category']
            constraints = self.CATEGORY_CONSTRAINTS.get(category, {})
            current = current_hours.get(category, 0)
            
            # Calculate needed hours
            daily_need = category_min['daily'] * total_days
            weekly_need = category_min['weekly'] * total_weeks
            monthly_need = category_min['monthly']
            needed_hours = max(daily_need, weekly_need, monthly_need) - current

            # Apply sleep maximum of 8 hours per day
            if category == 'Sleep':
                max_sleep_hours = 8 * total_days
                if current + needed_hours > max_sleep_hours:
                    needed_hours = max(0, max_sleep_hours - current)

            if needed_hours <= 0:
                continue

            # Ask AI for optimal scheduling strategy
            prompt = f"""
            Help schedule {needed_hours} hours of {category} with these constraints:
            - Preferred start time: {constraints.get('preferred_start_time', 'any')}
            - Preferred end time: {constraints.get('preferred_end_time', 'any')}
            - Must be consecutive hours: {constraints.get('consecutive_hours', False)}
            - Weekday only: {constraints.get('weekday_only', False)}
            - Current available slots: {len(available_slots)} slots
            
            Should we: 
            1. Schedule in larger blocks
            2. Split into smaller sessions
            3. Stick strictly to preferred times
            4. Be flexible with timing
            
            Respond with ONLY the number of your recommendation (1-4).
            """
            
            strategy = self.query_ollama(prompt)
            try:
                strategy = int(strategy.strip())
            except:
                strategy = 1  # Default to larger blocks if AI fails
                
            # Apply the strategy
            hours_to_fill = needed_hours
            available_slots = sorted(available_slots, key=lambda x: x[0])
            
            for start, end in available_slots:
                if hours_to_fill <= 0:
                    break
                    
                # Check constraints
                if constraints.get('weekday_only') and start.weekday() >= 5:
                    continue
                    
                slot_start_time = start.strftime('%H:%M')
                if (constraints.get('preferred_start_time') and 
                    slot_start_time < constraints['preferred_start_time']):
                    continue
                    
                if (constraints.get('preferred_end_time') and 
                    end.strftime('%H:%M') > constraints['preferred_end_time']):
                    continue
                
                slot_duration = (end - start).total_seconds() / 3600
                
                # Apply AI strategy
                if strategy == 1:  # Larger blocks
                    min_duration = 2.0  # Minimum 2 hours
                elif strategy == 2:  # Smaller sessions
                    min_duration = 0.5  # 30 minutes
                else:  # Strategy 3 or 4
                    min_duration = 1.0  # 1 hour
                
                if slot_duration >= min_duration:
                    hours_to_use = min(
                        slot_duration,
                        hours_to_fill if strategy != 2 else min(2.0, hours_to_fill)
                    )
                    
                    event_end = start + timedelta(hours=hours_to_use)
                    
                    # Create the event
                    self.create_new_event(
                        title=f"Scheduled {category}",
                        start_time=start,
                        end_time=event_end,
                        description=(f"Automatically scheduled to meet minimum hours\n"
                                   f"AI Strategy: {strategy}"),
                        category=category
                    )
                    
                    hours_to_fill -= hours_to_use
                    
                    # Update available slot
                    if hours_to_use < slot_duration:
                        available_slots.append((event_end, end))
            
            available_slots.sort(key=lambda x: x[0])

        return True

    def get_events_at_time(self, time):
        """Helper method to get events at a specific time"""
        if not self.google_service:
            raise Exception("Google Calendar not authenticated")
            
        calendar_list = self.google_service.calendarList().list().execute()
        testcal_id = next((cal['id'] for cal in calendar_list['items'] 
                          if cal['summary'] == 'testcal'), None)
        
        if testcal_id:
            events_result = self.google_service.events().list(
                calendarId=testcal_id,
                timeMin=(time - timedelta(minutes=1)).isoformat() + 'Z',
                timeMax=(time + timedelta(minutes=1)).isoformat() + 'Z',
                singleEvents=True
            ).execute()
            
            return [event.get('description', '') for event in events_result.get('items', [])]
        return []

    def update_available_slots(self, slots):
        """Helper method to update available slots after scheduling"""
        busy_slots = self.get_availability(slots[0][0], slots[-1][1])
        
        # Remove slots that are now occupied
        slots[:] = [(start, end) for start, end in slots 
                   if not any(busy_start <= start < busy_end 
                            for busy_start, busy_end in busy_slots)]
