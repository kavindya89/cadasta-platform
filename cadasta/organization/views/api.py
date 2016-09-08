from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework import generics, filters, status
from tutelary.mixins import APIPermissionRequiredMixin

from accounts.models import User

from ..models import Organization, OrganizationRole, ProjectRole
from .. import serializers
from . import mixins


class OrganizationList(APIPermissionRequiredMixin, generics.ListCreateAPIView):
    queryset = Organization.objects.all()
    serializer_class = serializers.OrganizationSerializer
    filter_backends = (filters.DjangoFilterBackend,
                       filters.SearchFilter,
                       filters.OrderingFilter,)
    filter_fields = ('archived',)
    search_fields = ('name', 'description',)
    ordering_fields = ('name', 'description',)
    permission_required = {
        'GET': 'org.list',
        'POST': 'org.create',
    }
    permission_filter_queryset = ('org.view',)


class OrganizationDetail(APIPermissionRequiredMixin,
                         generics.RetrieveUpdateAPIView):
    def patch_actions(self, request):
        if hasattr(request, 'data'):
            is_archived = self.get_object().archived
            new_archived = request.data.get('archived', is_archived)
            if not is_archived and (is_archived != new_archived):
                return ('org.update', 'org.archive')
            elif is_archived and (is_archived != new_archived):
                return ('org.update', 'org.unarchive')
            elif is_archived and (is_archived == new_archived):
                return False
        return 'org.update'

    queryset = Organization.objects.all()
    serializer_class = serializers.OrganizationSerializer
    lookup_field = 'slug'
    permission_required = {
        'GET': 'org.view',
        'PATCH': patch_actions,
    }


class OrganizationUsers(APIPermissionRequiredMixin,
                        mixins.OrganizationRoles,
                        generics.ListCreateAPIView):
    def update_permissions(self, request):
        if self.org.archived:
            return False
        return 'org.users.add'

    serializer_class = serializers.OrganizationUserSerializer
    permission_required = {
        'GET': 'org.users.list',
        'POST': update_permissions,
    }


class OrganizationUsersDetail(APIPermissionRequiredMixin,
                              mixins.OrganizationRoles,
                              generics.RetrieveUpdateDestroyAPIView):
    def update_permissions(self, view, request):
        if self.org.archived:
            return False
        return 'org.users.remove'

    serializer_class = serializers.OrganizationUserSerializer
    permission_required = update_permissions

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        if user == request.user:
            raise PermissionDenied
        OrganizationRole.objects.get(
            organization=self.org, user=user
        ).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class UserAdminList(APIPermissionRequiredMixin, generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.UserAdminSerializer
    filter_backends = (filters.DjangoFilterBackend,
                       filters.SearchFilter,
                       filters.OrderingFilter,)
    filter_fields = ('is_active',)
    search_fields = ('username', 'full_name', 'email')
    ordering_fields = ('username', 'full_name')
    permission_required = 'user.list'


class UserAdminDetail(APIPermissionRequiredMixin,
                      generics.RetrieveUpdateAPIView):
    serializer_class = serializers.UserAdminSerializer
    queryset = User.objects.all()
    lookup_field = 'username'
    permission_required = {
        'GET': 'user.list',
        'PATCH': 'user.update'
    }


class OrganizationProjectList(APIPermissionRequiredMixin,
                              mixins.OrganizationMixin,
                              mixins.ProjectQuerySetMixin,
                              generics.ListCreateAPIView):
    def update_permissions(self, request):
        if self.get_organization().archived:
            return False
        return 'project.create'

    serializer_class = serializers.ProjectSerializer
    filter_backends = (filters.DjangoFilterBackend,
                       filters.SearchFilter,
                       filters.OrderingFilter,)
    filter_fields = ('archived',)
    search_fields = ('name', 'organization__name', 'country', 'description',)
    ordering_fields = ('name', 'organization', 'country', 'description',)
    permission_required = {
        'GET': 'project.list',
        'POST': update_permissions
    }

    def get_serializer_context(self, *args, **kwargs):
        org = self.get_organization()
        context = super(OrganizationProjectList,
                        self).get_serializer_context(*args, **kwargs)
        context['organization'] = org

        return context

    def get_queryset(self):
        return super().get_queryset().filter(
            organization__slug=self.kwargs['slug']
        )


class ProjectList(APIPermissionRequiredMixin, mixins.ProjectQuerySetMixin,
                  generics.ListAPIView):
    serializer_class = serializers.ProjectSerializer
    filter_backends = (filters.DjangoFilterBackend,
                       filters.SearchFilter,
                       filters.OrderingFilter,)
    filter_fields = ('archived',)
    search_fields = ('name', 'organization__name', 'country', 'description',)
    ordering_fields = ('name', 'organization', 'country', 'description',)
    permission_required = {'project.list'}


class ProjectDetail(APIPermissionRequiredMixin,
                    mixins.OrganizationMixin,
                    generics.RetrieveUpdateDestroyAPIView):
    def get_actions(self, request):
        if self.get_object().public():
            return 'project.view'
        else:
            return 'project.view_private'

    def patch_actions(self, request):
        if hasattr(request, 'data'):
            is_archived = self.get_object().archived
            new_archived = request.data.get('archived', is_archived)
            if not is_archived and (is_archived != new_archived):
                return ('project.update', 'project.archive')
            elif is_archived and (is_archived != new_archived):
                return ('project.update', 'project.unarchive')
            elif is_archived and (is_archived == new_archived):
                return False
        return 'project.update'

    serializer_class = serializers.ProjectSerializer
    filter_fields = ('archived',)
    # search_fields = ('name', 'organization', 'country', 'description',)
    # ordering_fields = ('name', 'organization', 'country', 'description',)
    lookup_url_kwarg = 'project'
    lookup_field = 'slug'
    permission_required = {
        'GET': get_actions,
        'PATCH': patch_actions,
    }

    def get_perms_objects(self):
        return [self.get_object()]

    def get_queryset(self):
        return self.get_organization(
            lookup_kwarg='organization').projects.all()


class ProjectUsers(APIPermissionRequiredMixin,
                   mixins.ProjectRoles,
                   generics.ListCreateAPIView):
    def update_permissions(self, request):
        if self.get_project().archived:
            return False
        return 'project.users.add'

    serializer_class = serializers.ProjectUserSerializer
    permission_required = {
        'GET': 'project.users.list',
        'POST': update_permissions
    }


class ProjectUsersDetail(APIPermissionRequiredMixin,
                         mixins.ProjectRoles,
                         generics.RetrieveUpdateDestroyAPIView):
    def update_permissions(self, request):
        if self.get_project().archived:
            return False
        if request.method == 'PATCH':
            return 'project.users.edit'
        else:
            return 'project.users.delete'
    serializer_class = serializers.ProjectUserSerializer

    permission_required = {
        'GET': 'project.users.list',
        'PATCH': update_permissions,
        'DELETE': update_permissions,
    }

    def destroy(self, request, *args, **kwargs):
        ProjectRole.objects.get(
            project=self.prj, user=self.get_object()
        ).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
