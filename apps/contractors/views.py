from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import ContractorReview, ContractorProfile
from .serializers import ContractorReviewSerializer
from django.shortcuts import redirect
from django.views.generic import CreateView
from .forms import ContractorProfileForm

class ContractorReviewViewSet(viewsets.ModelViewSet):
    queryset = ContractorReview.objects.all()
    serializer_class = ContractorReviewSerializer
    permission_classes = [IsAuthenticated]

class ContractorRegisterView(CreateView):
    model = ContractorProfile
    form_class = ContractorProfileForm
    template_name = 'contractors/register.html'
    
    def form_valid(self, form):
        contractor = form.save(commit=False)
        # Предполагается, что пользователь уже аутентифицирован
        contractor.user = self.request.user
        contractor.registration_ip = self.request.META.get('REMOTE_ADDR')
        contractor.device_info = self.request.META.get('HTTP_USER_AGENT', '')
        contractor.save()
        return redirect('contractors:profile') 