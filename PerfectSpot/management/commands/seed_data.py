from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import random

from faker import Faker
from PerfectSpot.models import Event

User = get_user_model()


class Command(BaseCommand):
    help = "Seed the database with random users, events (in Poland), and random attendance"

    def handle(self, *args, **options):
        faker = Faker()
        NUM_USERS = 50
        NUM_EVENTS = 100

        # --- 1) Create random users ---
        users = []
        self.stdout.write("Deleting any existing users/events...")
        # (Uncomment below if you want to wipe data completely each run)
        # Event.objects.all().delete()
        # User.objects.exclude(is_superuser=True).delete()  # keep superuser if exists

        self.stdout.write("Creating users...")
        for _ in range(NUM_USERS):
            utype = random.choice(["individual", "organization"])
            username = faker.unique.user_name()
            email = faker.unique.email()
            password = "password123"

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                user_type=utype
            )
            if utype == "organization":
                user.organization_name = faker.company()
                user.is_org_verified = random.choice([True, False])
                user.save()

            users.append(user)

        self.stdout.write(self.style.SUCCESS(f"→ Created {len(users)} users."))

        # --- 2) Create random events ---
        events = []
        self.stdout.write("Creating events...")
        for _ in range(NUM_EVENTS):
            title = faker.sentence(nb_words=4)
            description = faker.paragraph(nb_sentences=3)
            location = f"{faker.city()}, Poland"

            # Poland’s approximate bounding box:
            latitude = round(random.uniform(49.0, 55.0), 6)
            longitude = round(random.uniform(14.0, 24.0), 6)

            # Random date: mix of past and future
            event_date = timezone.now() + timedelta(days=random.randint(-10, 60))

            creator = random.choice(users)
            is_promoted = (creator.user_type == "organization") and random.choice([True, False])

            image_url = faker.image_url(width=640, height=480)

            event = Event.objects.create(
                title=title,
                description=description,
                location=location,
                date=event_date,
                creator=creator,
                is_promoted=is_promoted,
                latitude=latitude,
                longitude=longitude,
                image_url=image_url
            )
            events.append(event)

        self.stdout.write(self.style.SUCCESS(f"→ Created {len(events)} events in Poland."))

        # --- 3) Randomly assign attendees to each event ---
        self.stdout.write("Assigning attendees to events...")
        for event in events:
            # Choose a random number of attendees between 0 and 10
            num_attendees = random.randint(0, 10)
            # Pick that many distinct users, excluding the creator
            possible_attendees = [u for u in users if u != event.creator]
            attendees_sample = random.sample(possible_attendees,
                                             min(len(possible_attendees), num_attendees))
            for attendee in attendees_sample:
                event.attendees.add(attendee)
            event.save()

        self.stdout.write(self.style.SUCCESS("→ Random attendance assignment complete."))
        self.stdout.write(self.style.SUCCESS("Database seed complete."))
