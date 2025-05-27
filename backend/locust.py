class HttpUser:
    pass


from locust import HttpUser, task, between
import random


class FastAPITestUser(HttpUser):
    wait_time = between(10, 15)  # Users wait between 3 and 8 seconds between tasks

    @task
    def predict_energy(self):
        # Generate random coordinates near a specific area (for example, Cary, NC)
        latitude = random.uniform(35.76, 35.79)
        longitude = random.uniform(-78.85, -78.79)

        payload = {"latitude": latitude, "longitude": longitude}

        response = self.client.post("/predict", json=payload)

        if response.status_code != 200:
            print(f"Error: {response.status_code}, Response: {response.text}")


def task():
    return None


def between():
    return None
