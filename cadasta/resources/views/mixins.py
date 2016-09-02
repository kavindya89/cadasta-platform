from django.core.urlresolvers import reverse
from django.http import Http404
from organization.views.mixins import ProjectMixin

from ..forms import ResourceForm
from ..models import Resource
from ..serializers import ReadOnlyResourceSerializer, ResourceSerializer


class ResourceViewMixin:
    form_class = ResourceForm
    serializer_class = ResourceSerializer

    def get_queryset(self):
        return self.get_content_object().resources.all()

    def get_model_context(self):
        return {
            'content_object': self.get_content_object(),
            'contributor': self.request.user
        }

    def get_serializer_context(self, *args, **kwargs):
        context = super().get_serializer_context(*args, **kwargs)
        context.update(self.get_model_context())
        return context

    def get_form_kwargs(self, *args, **kwargs):
        form_kwargs = super().get_form_kwargs(*args, **kwargs)
        form_kwargs.update(self.get_model_context())
        return form_kwargs

    def get_content_object(self):
        raise NotImplementedError('You need to implement get_content_object.')


class ProjectResourceMixin(ProjectMixin, ResourceViewMixin):

    def get_content_object(self):
        return self.get_project()

    def get_model_context(self):
        context = super().get_model_context()
        context['project_id'] = self.get_project().id
        return context

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['object'] = self.get_project()
        return context

    def get_success_url(self):
        project = self.get_project()

        next_url = self.request.GET.get('next', None)
        if next_url:
            return next_url + '#resources'

        return reverse(
            'resources:project_list',
            kwargs={
                'organization': project.organization.slug,
                'project': project.slug
            }
        )


class ResourceObjectMixin(ProjectResourceMixin):

    def get_object(self):
        try:
            return Resource.objects.get(
                project__slug=self.kwargs['project'],
                id=self.kwargs['resource']
            )
        except Resource.DoesNotExist as e:
            raise Http404(e)

    def get_perms_objects(self):
        return [self.get_object()]

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['resource'] = self.get_object()
        return context


class ProjectHasResourcesMixin(ProjectMixin):

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['project_has_resources'] = (
            self.get_project().resource_set.exists()
        )
        return context


class SpatialResourceViewMixin():
    serializer_class = ReadOnlyResourceSerializer

    def get_queryset(self):
        # only return Resources which have associated spatial resources
        project_id = self.get_content_object().id
        return Resource.objects.filter(
            project=project_id).exclude(spatial_resources=None)


class ProjectSpatialResourceMixin(ProjectMixin, SpatialResourceViewMixin):
    def get_content_object(self):
        return self.get_project()
