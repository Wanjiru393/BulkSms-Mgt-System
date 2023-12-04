import csv
from django.utils import timezone
from datetime import datetime
from django.http import HttpResponse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.parsers import FileUploadParser
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import SMSSerializer, SMSTemplateSerializer, UserProfileSerializer, UserProfileRegistrationSerializer
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .models import SMS, SMSTemplate, UserProfile
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from .models import PasswordResetToken, Customer
from django.contrib.auth.hashers import make_password


class UserRegistration(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserProfileRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            Token.objects.create(user=user) 
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLogin(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        staffnumber = request.data.get('staffnumber')
        password = request.data.get('password')
        if not staffnumber or not password:
            return Response({'error': 'Both staff number and password are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(userprofile__staff_number=staffnumber)
            if user.check_password(password):
                token, _ = Token.objects.get_or_create(user=user)
                return Response({'token': token.key})
        except UserModel.DoesNotExist:
            pass

        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)

class PasswordReset(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        staffnumber = request.data.get('staffnumber')
        if not staffnumber:
            return Response({'error': 'Staff number is required'}, status=status.HTTP_400_BAD_REQUEST)
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(userprofile__staff_number=staffnumber)
            token = get_random_string(length=32)
            PasswordResetToken.objects.create(user=user, token=token)
            send_mail(
                'Password Reset',
                f'Here is your password reset token: {token}',
                'cwanjiru393@gmail.com',
                [user.email],
                fail_silently=False,
            )
            return Response({'status': 'Password reset email sent'}, status=status.HTTP_200_OK)
        except UserModel.DoesNotExist:
            return Response({'error': 'Invalid Staff Number'}, status=status.HTTP_400_BAD_REQUEST)
    

class PasswordResetConfirm(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get('token')
        new_password = request.data.get('new_password')
        try:
            password_reset_token = PasswordResetToken.objects.get(token=token)
            user = password_reset_token.user
            user.password = make_password(new_password)
            user.save()
            password_reset_token.delete()
            return Response({'status': 'Password reset successful'}, status=status.HTTP_200_OK)
        except PasswordResetToken.DoesNotExist:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT'])
@permission_classes([IsAdminUser])
def manage_user_roles(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
        user_profile = user.userprofile

        if request.method == 'GET':
            serializer = UserProfileSerializer(user_profile)
            return Response(serializer.data)

        elif request.method == 'PUT':
            new_role = request.data.get('role')
            if new_role not in dict(UserProfile.ROLE_CHOICES):
                return Response({'error': 'Invalid role'}, status=status.HTTP_400_BAD_REQUEST)
            user_profile.role = new_role
            user_profile.save()
            return Response({'status': 'role updated'}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)
    

class FileUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_class = (FileUploadParser,)

    def post(self, request):
        file = request.data['file']
        decoded_file = file.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded_file)
        data = []
        for row in reader:
            customer = Customer.objects.create(
                name=row['Full Name'],
                contact=row['Phone Number'],
                account_number=row['Acc Number']
            )
            data.append({
                'id': customer.id,
                'name': customer.name,
                'contact': customer.contact,
                'account_number': customer.account_number
            })
        return Response(data, status=status.HTTP_201_CREATED)
    
class SMSTemplateListView(APIView):

    def get(self, request):
        templates = SMSTemplate.objects.all()
        serializer = SMSTemplateSerializer(templates, many=True)
        return Response(serializer.data)

class SMSTemplateCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SMSTemplateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SMSTemplateUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        template = SMSTemplate.objects.get(pk=pk)
        serializer = SMSTemplateSerializer(template, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class SMSTemplateDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            template = SMSTemplate.objects.get(pk=pk)
            template.delete()
            return Response({'status': 'Template deleted'}, status=status.HTTP_200_OK)
        except SMSTemplate.DoesNotExist:
            return Response({'error': 'Template does not exist'}, status=status.HTTP_404_NOT_FOUND)

class SMSCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SMSSerializer(data=request.data)
        if serializer.is_valid():
            sms = serializer.save(created_by=request.user)
            return Response(SMSSerializer(sms).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class SMSEditView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        try:
            sms = SMS.objects.get(pk=pk)
            serializer = SMSSerializer(sms, data=request.data, partial=True)
            if serializer.is_valid():
                sms = serializer.save(created_by=request.user)
                serializer.update_message_content(sms)
                sms.submission_date = timezone.now()
                sms.save()
                return Response(SMSSerializer(sms).data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except SMS.DoesNotExist:
            return Response({'error': 'SMS does not exist'}, status=status.HTTP_404_NOT_FOUND)


class SMSDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            sms = SMS.objects.get(pk=pk)
            sms.is_deleted = True
            sms.save()
            return Response({'status': 'SMS marked as deleted'}, status=status.HTTP_200_OK)
        except SMS.DoesNotExist:
            return Response({'error': 'SMS does not exist'}, status=status.HTTP_404_NOT_FOUND)
        
class SMSListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        sms = SMS.objects.filter(is_deleted=False)
        serializer = SMSSerializer(sms, many=True)
        return Response(serializer.data)


class SMSDeletedListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        sms = SMS.objects.filter(is_deleted=True)
        serializer = SMSSerializer(sms, many=True)
        return Response(serializer.data)


class SMSRestoreView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        try:
            sms = SMS.objects.get(pk=pk, is_deleted=True)
            sms.is_deleted = False
            sms.save()
            return Response({'status': 'SMS restored'}, status=status.HTTP_200_OK)
        except SMS.DoesNotExist:
            return Response({'error': 'SMS does not exist or is not deleted'}, status=status.HTTP_404_NOT_FOUND)
        
class SMSApprovalView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        if request.user.userprofile.role != 'approver':
            return Response({'error': 'Only approvers can approve SMS'}, status=status.HTTP_403_FORBIDDEN)

        try:
            sms = SMS.objects.get(pk=pk)
        except SMS.DoesNotExist:
            return Response({'error': 'SMS does not exist'}, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get('approval_status')
        if new_status not in dict(SMS.APPROVAL_STATUS_CHOICES):
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
        
        sms.approval_status = new_status
        sms.approved_by = request.user

        sms.save()

        return Response({'status': 'SMS status updated'}, status=status.HTTP_200_OK)
    

class ApprovedSMSView(APIView):

    def get(self, request):
        approved_sms = SMS.objects.filter(approval_status='approved')
        serializer = SMSSerializer(approved_sms, many=True)
        return Response(serializer.data)


class RejectedSMSView(APIView):

    def get(self, request):
        rejected_sms = SMS.objects.filter(approval_status='rejected')
        serializer = SMSSerializer(rejected_sms, many=True)
        return Response(serializer.data)