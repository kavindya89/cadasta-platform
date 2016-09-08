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
    permission_filter_queryset = (lambda self, view, o: ('org.view',)
                                  if o.archived is False
                                  else ('org.view_archived',))

    # def get_queryset(self):
    #     user = self.request.user
    #     if hasattr(user, 'assigned_policies'):
    #             role = Role.objects.filter(name='superuser')
    #             if len(role) > 0:
    #                 if role[0] in self.request.user.assigned_policies():
    #                     return Organization.objects.all()
    #     organizations = Organization.objects.all()
    #     if hasattr(user, 'organizations'):
    #         for org in Organization.objects.all():
    #             if org not in user.organizations.all():
    #                 organizations = organizations.exclude(access='private',
    #                                                       name=org.name)
    #             elif OrganizationRole.objects.get(organization=org,
    #                                               user=user
    #                                               ).admin is False:
    #                     organizations = organizations.exclude(archived=True,
    #                                                           name=org.name)
    #     return organizations


class OrganizationDetail(APIPermissionRequiredMixin,
                         mixins.OrganizationMixin,
                         generics.RetrieveUpdateAPIView):
    def view_actions(self, request):
        if self.get_object().archived:
            return 'org.view_archived'
        return 'org.view'

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
        'GET': view_actions,
        'PATCH': patch_actions,
    }


def update_permissions(permission):
        def set_permissions(self, request, view=None):
            if hasattr(self, "get_organization"):
                if self.get_organization().archived:
                    return False
            if hasattr(self, "get_project"):
                if self.get_project().archived:
                    print('return False')
                    return False
            return permission
        return set_permissions


class OrganizationUsers(APIPermissionRequiredMixin,
                        mixins.OrganizationRoles,
                        generics.ListCreateAPIView):
    serializer_class = serializers.OrganizationUserSerializer
    permission_required = {
        'GET': 'org.users.list',
        'POST': update_permissions('org.users.add'),
    }


class OrganizationUsersDetail(APIPermissionRequiredMixin,
                              mixins.OrganizationRoles,
                              generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.OrganizationUserSerializer
    permission_required = update_permissions('org.users.remove')

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
                              mixins.OrgAdminCheckMixin,
                              mixins.ProjectQuerySetMixin,
                              generics.ListCreateAPIView):
    serializer_class = serializers.ProjectSerializer
    filter_backends = (filters.DjangoFilterBackend,
                       filters.SearchFilter,
                       filters.OrderingFilter,)
    filter_fields = ('archived',)
    search_fields = ('name', 'organization__name', 'country', 'description',)
    ordering_fields = ('name', 'organization', 'country', 'description',)
    permission_required = {
        'GET': 'project.list',
        'POST': update_permissions('project.create')
    }

    def get_serializer_context(self, *args, **kwargs):
        org = self.get_organization()
        context = super(OrganizationProjectList,
                        self).get_serializer_context(*args, **kwargs)
        context['organization'] = org

        return context

    def get_queryset(self):
        if self.is_administrator:
            return super().get_queryset().filter(
                organization__slug=self.kwargs['slug']
            )
        else:
            return super().get_queryset().filter(
                organization__slug=self.kwargs['slug'],
                archived=False, access='public'
            )


class ProjectList(APIPermissionRequiredMixin,
                  mixins.ProjectQuerySetMixin,
                  generics.ListAPIView):
    def permission_filter(self, view, p):
        if p.access == 'public' and p.archived is False:
            return ('project.view',)
        elif p.archived is True:
            return ('project.view_archived',)
        else:
            return ('project.view_private',)

    serializer_class = serializers.ProjectSerializer
    filter_backends = (filters.DjangoFilterBackend,
                       filters.SearchFilter,
                       filters.OrderingFilter,)
    filter_fields = ('archived',)
    search_fields = ('name', 'organization__name', 'country', 'description',)
    ordering_fields = ('name', 'organization', 'country', 'description',)
    permission_required = {'GET': 'project.list'}
    permission_filter_queryset = permission_filter


class ProjectDetail(APIPermissionRequiredMixin,
                    mixins.OrganizationMixin,
                    generics.RetrieveUpdateDestroyAPIView):
    def get_actions(self, request):
        if self.get_object().archived:
            return 'project.view_archived'
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

    serializer_class = serializers.ProjectUserSerializer
    permission_required = {
        'GET': 'project.users.list',
        'POST': update_permissions('project.users.add')
    }


class ProjectUsersDetail(APIPermissionRequiredMixin,
                         mixins.ProjectRoles,
                         generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.ProjectUserSerializer

    permission_required = {
        'GET': 'project.users.list',
        'PATCH': update_permissions('project.users.update'),
        'DELETE': update_permissions('project.users.delete'),
    }

    def destroy(self, request, *args, **kwargs):
        ProjectRole.objects.get(
            project=self.prj, user=self.get_object()
        ).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
