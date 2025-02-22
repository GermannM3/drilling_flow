from locust import HttpUser, task, between

class DrillFlowUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def view_contractors(self):
        self.client.get("/api/contractors/nearby", 
            params={"lat": 55.7558, "lng": 37.6173})
    
    @task(2)
    def create_order(self):
        self.client.post("/api/orders/", json={
            "service_type": "drilling",
            "address": "Test Address",
            "description": "Test Order"
        }) 