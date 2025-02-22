from rest_framework.views import APIView
from rest_framework.response import Response
from .services import GeocodingService

class GeocodeView(APIView):
    def get(self, request):
        address = request.query_params.get('address')
        if not address:
            return Response({'error': 'Address is required'}, status=400)
            
        service = GeocodingService()
        result = service.geocode_address(address)
        
        if result:
            return Response(result)
        return Response({'error': 'Could not geocode address'}, status=400)

class ReverseGeocodeView(APIView):
    def get(self, request):
        lat = request.query_params.get('lat')
        lng = request.query_params.get('lng')
        
        if not all([lat, lng]):
            return Response({'error': 'Latitude and longitude are required'}, status=400)
            
        service = GeocodingService()
        address = service.reverse_geocode(float(lat), float(lng))
        
        if address:
            return Response({'address': address})
        return Response({'error': 'Could not reverse geocode coordinates'}, status=400) 